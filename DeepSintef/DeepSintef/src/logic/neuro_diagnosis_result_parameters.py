import json
import collections
import operator


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
        self.tumor_parts = self.json_content['Overall']['Components']

        self.statistics = {}
        self.statistics['Main'] = {}
        self.statistics['Main']['Overall'] = TumorStatistics()
        self.statistics['Main']['CoM'] = TumorStatistics()

        self.statistics['Main']['CoM'].laterality = self.json_content['Main']['CenterOfMass']['Laterality']
        self.statistics['Main']['CoM'].laterality_percentage = self.json_content['Main']['CenterOfMass']['Laterality_perc']
        lobes_overlap = {item[0]: item[1] for item in self.json_content['Main']['CenterOfMass']['Lobe']}
        lobes_overlap_o = collections.OrderedDict(sorted(lobes_overlap.items(), key=operator.itemgetter(1), reverse=True))
        self.statistics['Main']['CoM'].mni_space_lobes_overlap = lobes_overlap_o

        self.statistics['Main']['Overall'].laterality = self.json_content['Main']['Total']['Laterality']
        self.statistics['Main']['Overall'].laterality_percentage = self.json_content['Main']['Total']['Laterality_perc']
        self.statistics['Main']['Overall'].mni_space_tumor_volume = self.json_content['Main']['Total']['Volume']
        self.statistics['Main']['Overall'].mni_space_resectability_score = self.json_content['Main']['Total']['Resectability']

        lobes_overlap = {item[0]: item[1] for item in self.json_content['Main']['Total']['Lobe']}
        lobes_overlap_o = collections.OrderedDict(sorted(lobes_overlap.items(), key=operator.itemgetter(1), reverse=True))
        self.statistics['Main']['Overall'].mni_space_lobes_overlap = lobes_overlap_o

        tracts_overlap = {item[0]: item[1] for item in self.json_content['Main']['Total']['Tract']['Overlap']}
        tracts_overlap_o = collections.OrderedDict(sorted(tracts_overlap.items(), key=operator.itemgetter(1), reverse=True))
        self.statistics['Main']['Overall'].mni_space_tracts_overlap = tracts_overlap_o

        tracts_dist = {item[0]: item[1] for item in self.json_content['Main']['Total']['Tract']['Distance']}
        tracts_dist_o = collections.OrderedDict(sorted(tracts_dist.items(), key=operator.itemgetter(1), reverse=False))
        self.statistics['Main']['Overall'].mni_space_tracts_distance = tracts_dist_o

        if self.tumor_multifocal:
            for p in range(self.tumor_parts):
                pname = str(p + 1)
                self.statistics[pname] = {}
                self.statistics[pname]['Overall'] = TumorStatistics()
                self.statistics[pname]['CoM'] = TumorStatistics()

                self.statistics[pname]['Overall'].laterality = self.json_content[pname]['Total']['Laterality']
                self.statistics[pname]['Overall'].laterality_percentage = self.json_content[pname]['Total']['Laterality_perc']
                self.statistics[pname]['Overall'].mni_space_tumor_volume = self.json_content[pname]['Total']['Volume']
                self.statistics[pname]['Overall'].mni_space_resectability_score = self.json_content[pname]['Total']['Resectability']

                lobes_overlap = {item[0]: item[1] for item in self.json_content[pname]['Total']['Lobe']}
                lobes_overlap_o = collections.OrderedDict(
                    sorted(lobes_overlap.items(), key=operator.itemgetter(1), reverse=True))
                self.statistics[pname]['Overall'].mni_space_lobes_overlap = lobes_overlap_o

                tracts_overlap = {item[0]: item[1] for item in self.json_content[pname]['Total']['Tract']['Overlap']}
                tracts_overlap_o = collections.OrderedDict(
                    sorted(tracts_overlap.items(), key=operator.itemgetter(1), reverse=True))
                self.statistics[pname]['Overall'].mni_space_tracts_overlap = tracts_overlap_o

                tracts_dist = {item[0]: item[1] for item in self.json_content[pname]['Total']['Tract']['Distance']}
                tracts_dist_o = collections.OrderedDict(
                    sorted(tracts_dist.items(), key=operator.itemgetter(1), reverse=False))
                self.statistics[pname]['Overall'].mni_space_tracts_distance = tracts_dist_o


class TumorStatistics():
    def __init__(self):
        self.laterality = None
        self.laterality_percentage = None
        self.mni_space_resectability_score = None
        self.mni_space_tumor_volume = None
        self.mni_space_lobes_overlap = {}
        self.mni_space_tracts_overlap = {}
        self.mni_space_tracts_distance = {}