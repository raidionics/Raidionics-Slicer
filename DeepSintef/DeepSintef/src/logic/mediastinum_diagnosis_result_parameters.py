import json
import collections
import operator


class MediastinumDiagnosisParameters:
    """
    Singleton class to have access from anywhere in the code at the various parameters linked to a mediastinum diagnosis.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if MediastinumDiagnosisParameters.__instance == None:
            MediastinumDiagnosisParameters()
        return MediastinumDiagnosisParameters.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if MediastinumDiagnosisParameters.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MediastinumDiagnosisParameters.__instance = self

    def clear(self):
        self.statistics = {}

    def from_json(self, filename):
        self.clear()
        with open(filename, 'r') as pfile:
            self.json_content = json.load(pfile)

        self.lymphnodes_count = self.json_content['Overall']['Lymphnodes_count']

        self.statistics = {}
        self.statistics['LymphNodes'] = {}
        for p in range(self.lymphnodes_count):
            pname = str(p + 1)
            self.statistics['LymphNodes'][pname] = LymphNodeStatistics()
            self.statistics['LymphNodes'][pname].volume = self.json_content['LymphNodes'][pname]['Volume']
            self.statistics['LymphNodes'][pname].axis_diameters = self.json_content['LymphNodes'][pname]['Axis_diameters']


class LymphNodeStatistics():
    def __init__(self):
        self.laterality = None
        self.volume = None
        self.axis_diameters = []
        self.stations_overlap = {}
