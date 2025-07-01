import os
from os.path import expanduser
import shutil
try:
    import configparser
except:
    from __main__ import slicer
    slicer.util.pip_install('configparser')
    import configparser


class SharedResources:
    """
    Singleton class to have access from anywhere in the code at the various local paths where the data, or code are
    located.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if SharedResources.__instance == None:
            SharedResources()
        return SharedResources.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if SharedResources.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SharedResources.__instance = self

    def set_environment(self):
        self.home_path = expanduser("~")
        current_folder = os.path.dirname(os.path.realpath(__file__))
        self.icon_dir = os.path.join(current_folder, '../../', '/Resources/Icons/')

        self.Raidionics_dir = os.path.join(self.home_path, '.raidionics-slicer')
        if not os.path.isdir(self.Raidionics_dir):
            os.mkdir(self.Raidionics_dir)

        self.json_cloud_dir = os.path.join(self.Raidionics_dir, 'json', 'cloud')
        if os.path.isdir(self.json_cloud_dir):
            shutil.rmtree(self.json_cloud_dir)
        os.makedirs(self.json_cloud_dir)
        # @OBS. Unused under?
        self.json_cloud_info_file = "https://github.com/raidionics/Raidionics-models/releases/download/v1.3.0-rc/Slicer_cloud_models_list_v13.csv" #"https://drive.google.com/uc?id=13-Mx1Os9eXB_bJBcJt_o9MXQrRI1xONi"

        self.json_local_dir = os.path.join(self.Raidionics_dir, 'json', 'local')
        if not os.path.isdir(self.json_local_dir):
            os.makedirs(self.json_local_dir)

        self.resources_path = os.path.join(self.Raidionics_dir, 'resources')

        self.model_path = os.path.join(self.resources_path, 'models')
        if not os.path.isdir(self.model_path):
            os.makedirs(self.model_path)

        self.diagnosis_path = os.path.join(self.resources_path, 'reporting')
        if not os.path.isdir(self.diagnosis_path):
            os.makedirs(self.diagnosis_path)

        self.data_path = os.path.join(self.resources_path, 'data')
        if os.path.isdir(self.data_path):
            shutil.rmtree(self.data_path)
        os.makedirs(self.data_path)

        self.user_config_filename = os.path.join(self.data_path, 'runtime_config.ini')
        self.diagnosis_config_filename = os.path.join(self.data_path, 'diagnosis_config.ini')

        self.output_path = os.path.join(self.resources_path, 'output')
        if os.path.isdir(self.output_path):
            shutil.rmtree(self.output_path)
        os.makedirs(self.output_path)

        self.docker_path = None
        self.__set_runtime_parameters()
        self.global_active_model_update = False
        self.__set_default_stylesheet_components()

    def __set_runtime_parameters(self):
        # Most likely deprecated, as we moved from the seg backend to the rads one!
        # Set of variables sent to the docker images as runtime config, manually chosen by the user.
        self.user_configuration = configparser.ConfigParser()
        self.user_configuration['Predictions'] = {}
        self.user_configuration['Predictions']['non_overlapping'] = 'true'
        self.user_configuration['Predictions']['reconstruction_method'] = 'probabilities'
        self.user_configuration['Predictions']['reconstruction_order'] = 'resample_first'
        self.user_configuration['Runtime'] = {}
        self.user_configuration['Runtime']['use_stripped_data'] = 'False'
        self.user_configuration['Runtime']['use_registered_data'] = 'False'
        self.user_configuration['Neuro'] = {}
        self.user_configuration['Neuro']['brain_segmentation_filename'] = ''
        self.user_configuration['Mediastinum'] = {}
        self.user_configuration['Mediastinum']['lungs_segmentation_filename'] = ''
        self.use_gpu = False

        self.user_diagnosis_configuration = configparser.ConfigParser()
        self.user_diagnosis_configuration['Default'] = {}
        self.user_diagnosis_configuration['Default']['task'] = 'neuro_diagnosis'
        self.user_diagnosis_configuration['Default']['trace'] = 'false'
        self.user_diagnosis_configuration['Default']['from_slicer'] = 'true'
        self.user_diagnosis_configuration['Neuro'] = {}
        self.user_diagnosis_configuration['Neuro']['tumor_segmentation_filename'] = ''
        self.user_diagnosis_configuration['Neuro']['brain_segmentation_filename'] = ''

    def __set_default_stylesheet_components(self):
        self.stylesheet_components = {}
        self.stylesheet_components["Color1"] = "rgba(0, 0, 0, 1)"  # Black
        self.stylesheet_components["Color2"] = "rgba(235, 250, 255, 1)"  # Main background color (blueish white)
        self.stylesheet_components["Color3"] = "rgba(239, 255, 245, 1)"  # Light green
        self.stylesheet_components["Color4"] = "rgba(209, 241, 222, 1)"  # Darker light green (when pressed)
        self.stylesheet_components["Color5"] = "rgba(248, 248, 248, 1)"  # Almost white (standard background)
        self.stylesheet_components["Color6"] = "rgba(214, 214, 214, 1)"  # Darker almost white (when pressed)
        self.stylesheet_components["Color7"] = "rgba(67, 88, 90, 1)"  # Main font color ()

        self.stylesheet_components["White"] = "rgba(255, 255, 255, 1)"  # White
        self.stylesheet_components["Process"] = "rgba(255, 191, 128, 1)"  # Light orange
        self.stylesheet_components["Process_pressed"] = "rgba(204, 102, 0, 1)"  # Dark orange
        self.stylesheet_components["Import"] = "rgba(73, 99, 171, 1)"  # Greyish blue
        self.stylesheet_components["Import_pressed"] = "rgba(81, 101, 153, 1)"  # Dark greyish blue
        self.stylesheet_components["Data"] = "rgba(204, 224, 255, 1)"  # Greyish blue
        self.stylesheet_components["Background_pressed"] = "rgba(0, 120, 230, 1)"  # Dark blue