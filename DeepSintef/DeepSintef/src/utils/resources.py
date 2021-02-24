import os
from os.path import expanduser
import shutil


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

        self.deepsintef_dir = os.path.join(self.home_path, '.deepsintef')
        if not os.path.isdir(self.deepsintef_dir):
            os.mkdir(self.deepsintef_dir)

        self.json_cloud_dir = os.path.join(self.deepsintef_dir, 'json', 'cloud')
        if os.path.isdir(self.json_cloud_dir):
            shutil.rmtree(self.json_cloud_dir)
        os.makedirs(self.json_cloud_dir)

        self.json_local_dir = os.path.join(self.deepsintef_dir, 'json', 'local')
        if not os.path.isdir(self.json_local_dir):
            os.makedirs(self.json_local_dir)

        self.resources_path = os.path.join(self.deepsintef_dir, 'resources')

        self.tmp_path = os.path.join(self.resources_path, 'data')
        if os.path.isdir(self.tmp_path):
            shutil.rmtree(self.tmp_path)
        os.makedirs(self.tmp_path)

        self.user_config = os.path.join(self.tmp_path, 'runtime_config.ini')

        self.docker_path = None
