import configparser
import os
import json
import traceback

from src.utils.resources import SharedResources


def generate_segmentation_pipeline(model_name: str, tumor_type: str) -> dict:
    """

    """
    ts = 0
    pip = {}
    pip_num_int = 0

    all_models = [x.strip() for x in model_name.split(',')]
    for model in all_models:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Model selection'
        pip[pip_num]["model"] = model
        pip[pip_num]["timestamp"] = ts
        pip[pip_num]["format"] = "probabilities" if len(all_models) == 1 else "thresholding"
        pip[pip_num]["description"] = f"Identifying the best segmentation model for existing inputs for {model}"
    if len(all_models) > 1:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Segmentation refinement'
        pip[pip_num]["inputs"] = {}
        pip[pip_num]["inputs"]["0"] = {}
        pip[pip_num]["inputs"]["0"]["timestamp"] = ts
        pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE" if tumor_type == "Contrast-Enhancing" else "FLAIR"
        pip[pip_num]["inputs"]["0"]["labels"] = "Tumor"
        pip[pip_num]["inputs"]["0"]["space"] = {}
        pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = ts
        pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE" if tumor_type == "Contrast-Enhancing" else "FLAIR"
        pip[pip_num]["operation"] = "global_context"
        pip[pip_num]["args"] = {}
        pip[pip_num]["description"] = f"Global segmented structures context refinement."

    return pip


def generate_reporting_pipeline(task, tumor_type):
    pip = {}
    pip_num_int = 0

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = ""
    pip[pip_num]["timestamp"] = 0
    pip[pip_num]["format"] = "probabilities"
    pip[pip_num]["description"] = "Identifying the best tumor core segmentation model for existing inputs"

def generate_backend_config(input_folder: str, parameters, logic_target_space: str, logic_task: str,
                            model_name: str, json_params: dict) -> None:
    """
    Preparing the configuration file to be used as input by raidionics_rads_lib (processing backend).

    Parameters
    ----------
    input_folder: str
         Folder to be used as input by the backend.
    parameters: ?
        Not used anymore
    logic_target_space: str
        Description of the targeted medical specialty, between neuro and mediastinum for now.
    logic_task: str
        Disambiguation between single segmentation or complex diagnosis pipeline
    model_name: str
        Name of the model to be executed in the backend.
    """
    try:
        rads_config = configparser.ConfigParser()
        rads_config.add_section('Default')
        rads_config.set('Default', 'task', logic_target_space)
        rads_config.set('Default', 'caller', '')
        rads_config.add_section('System')
        rads_config.set('System', 'gpu_id', "-1")  # Always running on CPU
        rads_config.set('System', 'input_folder', '/workspace/resources/data')
        rads_config.set('System', 'output_folder', '/workspace/resources/output')
        rads_config.set('System', 'model_folder', '/workspace/resources/models')
        if logic_task == "segmentation":
            pipeline = generate_segmentation_pipeline(model_name=model_name, tumor_type=json_params['tumor_type'])
        elif logic_task == "complex_diagnosis":
            pipeline = generate_reporting_pipeline(task=None, tumor_type=json_params['tumor_type'])
        pipeline_filename = os.path.join(input_folder, 'rads_pipeline.json')
        with open(pipeline_filename, 'w', newline='\n') as outfile:
            json.dump(pipeline, outfile, indent=4)
        rads_config.set('System', 'pipeline_filename', '/workspace/resources/data/rads_pipeline.json')
        if logic_task == 'reporting':
            rads_config.set('System', 'pipeline_filename',
                            '/workspace/resources/reporting/' + parameters['UserConfiguration']['default'])
        rads_config.add_section('Runtime')
        rads_config.set('Runtime', 'reconstruction_method',
                        SharedResources.getInstance().user_configuration['Predictions']['reconstruction_method'])
        rads_config.set('Runtime', 'reconstruction_order',
                        SharedResources.getInstance().user_configuration['Predictions']['reconstruction_order'])
        rads_config.set('Runtime', 'use_stripped_data',
                        SharedResources.getInstance().user_configuration['Runtime']['use_stripped_data'])
        rads_config.set('Runtime', 'use_registered_data',
                        SharedResources.getInstance().user_configuration['Runtime']['use_registered_data'])
        # @TODO. Add a user option to include/exclude atlases
        rads_config.add_section('Neuro')
        rads_config.set('Neuro', 'cortical_features', 'MNI, Schaefer7, Schaefer17, Harvard-Oxford')
        rads_config.set('Neuro', 'subcortical_features', 'BCB')
        rads_config_filename = os.path.join(input_folder, 'rads_config.ini')
        with open(rads_config_filename, 'w') as outfile:
            rads_config.write(outfile)
    except Exception:
        print("Backend config file creation failed.")
        print(traceback.format_exc())


def postop_model_selection(inputs: dict) -> str:
    model_name = "MRI_GBM_Postop_FV_4p"
    if inputs["T1w postop"] is None and inputs["FLAIR postop"] is None and inputs["T1wCE preop"] is None:
        model_name = "MRI_GBM_Postop_FV_1p"
    elif inputs["FLAIR postop"] is None and inputs["T1wCE preop"] is None:
        model_name = "MRI_GBM_Postop_FV_2p"
    elif inputs["T1wCE preop"] is None:
        model_name = "MRI_GBM_Postop_FV_3p"
    elif inputs["FLAIR postop"] is None and inputs["T1wCE preop"] is not None:
        model_name = "MRI_GBM_Postop_FV_4p"
    else:
        model_name = "MRI_GBM_Postop_FV_5p"

    return model_name
