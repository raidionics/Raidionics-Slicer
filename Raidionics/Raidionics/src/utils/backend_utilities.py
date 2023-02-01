import configparser
import os
import json


def generate_backend_config(input_folder, parameters):
    pipeline_filename = parameters["UserConfiguration"]["pipeline_name"]
    rads_config = configparser.ConfigParser()
    rads_config.add_section('Default')
    rads_config.set('Default', 'task', 'neuro_diagnosis')
    rads_config.set('Default', 'caller', '')
    rads_config.add_section('System')
    rads_config.set('System', 'gpu_id', "-1")  # Always running on CPU
    rads_config.set('System', 'input_folder', '/home/ubuntu/resources/data')
    rads_config.set('System', 'output_folder', '/home/ubuntu/resources/output')
    rads_config.set('System', 'model_folder', '/home/ubuntu/resources/models')
    # pipeline = create_backend_pipeline()
    # pipeline_filename = os.path.join(input_folder, 'rads_pipeline.json')
    # with open(pipeline_filename, 'w', newline='\n') as outfile:
    #     json.dump(pipeline, outfile, indent=4)
    rads_config.set('System', 'pipeline_filename', os.path.join('/home/ubuntu/resources/pipelines', pipeline_filename))
    rads_config.add_section('Runtime')
    rads_config.set('Runtime', 'reconstruction_method', 'thresholding')
    rads_config.set('Runtime', 'reconstruction_order', 'resample_first')
    # rads_config.add_section('Neuro')
    # if SoftwareConfigResources.getInstance().user_preferences.compute_cortical_structures:
    #     rads_config.set('Neuro', 'cortical_features', 'MNI, Schaefer7, Schaefer17, Harvard-Oxford')
    # if SoftwareConfigResources.getInstance().user_preferences.compute_subcortical_structures:
    #     rads_config.set('Neuro', 'subcortical_features', 'BCB')
    rads_config_filename = os.path.join(input_folder, 'rads_config.ini')
    with open(rads_config_filename, 'w') as outfile:
        rads_config.write(outfile)


def create_backend_pipeline():
    pip = {}
    pip_num_int = 0

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "FLAIR" #"T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "FLAIR" #"T1-CE"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1CE (T0)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "FLAIR" #"T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "FLAIR" #"T1-CE"
    pip[pip_num]["target"] = ["Tumor"]
    pip[pip_num]["model"] = "MRI_LGGlioma"
    pip[pip_num]["description"] = "Tumor segmentation in T1CE (T0)"

    return pip
