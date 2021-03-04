import json


class NeuroDiagnosisParameters:
    """
    Singleton class to have access from anywhere in the code at the various parameters linked to a neuro diagnosis.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if NeuroDiagnosisParameters.__instance == None:
            NeuroDiagnosisParameters()
        return NeuroDiagnosisParameters.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if NeuroDiagnosisParameters.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            NeuroDiagnosisParameters.__instance = self

    def clear(self):
        self.tumor_presence_state = False
        self.tumor_type = None
        self.tumor_multifocal = False
        self.statistics = {}

    def from_json(self, filename):
        self.clear()
        with open(filename, 'r') as pfile:
            self.json_content = json.load(pfile)

        self.tumor_presence_state = self.json_content['Overall']['Presence']
        self.tumor_type = self.json_content['Overall']['Type']
        self.tumor_multifocal = self.json_content['Overall']['Multifocal']
        # self.tumor_parts = tumor_elements

        self.statistics = {}
        self.statistics['Main'] = {}
        self.statistics['Main']['Overall'] = TumorStatistics()
        self.statistics['Main']['CoM'] = TumorStatistics()

        self.statistics['Main']['Overall'].laterality = self.json_content['Main']['Total']['Laterality']
        self.statistics['Main']['Overall'].mni_space_tumor_volume = self.json_content['Main']['Total']['Volume']


class TumorStatistics():
    def __init__(self):
        self.laterality = None
        self.laterality_percentage = None
        self.mni_space_tumor_volume = None
        self.mni_space_lobes_overlap = {}
        self.mni_space_tracts_overlap = {}
        self.mni_space_tracts_distance = {}