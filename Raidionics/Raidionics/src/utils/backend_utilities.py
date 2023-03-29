import configparser
import os
import json
import traceback

from src.utils.resources import SharedResources


def generate_backend_config(input_folder: str, parameters, logic_target_space: str, logic_task: str,
                            model_name: str) -> None:
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
        rads_config.set('System', 'input_folder', '/home/ubuntu/resources/data')
        rads_config.set('System', 'output_folder', '/home/ubuntu/resources/output')
        rads_config.set('System', 'model_folder', '/home/ubuntu/resources/models')
        rads_config.set('System', 'pipeline_filename', '/home/ubuntu/resources/models/' + model_name + '/pipeline.json')
        if logic_task == 'diagnosis':
            rads_config.set('System', 'pipeline_filename',
                            '/home/ubuntu/resources/diagnosis/' + parameters['UserConfiguration']['default'])
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
