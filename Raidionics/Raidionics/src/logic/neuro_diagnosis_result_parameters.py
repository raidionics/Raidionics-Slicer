import json
import collections
import logging
import operator
import traceback


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
        self.tumor_parts = 0
        self.tumor_multifocal_distance = -1.
        self.statistics = {}

    def from_json(self, filename):
        try:
            self.clear()
            with open(filename, 'r') as pfile:
                self.json_content = json.load(pfile)

            self.tumor_presence_state = self.json_content['Overall']['Presence'] if "Presence" in list(self.json_content['Overall'].keys()) else None
            self.tumor_type = self.json_content['Overall']['Type'] if "Type" in list(self.json_content['Overall'].keys()) else None
            self.tumor_multifocal = self.json_content['Overall']['Multifocality'] if "Multifocality" in list(self.json_content['Overall'].keys()) else None
            self.tumor_parts = self.json_content['Overall']['Tumor parts nb'] if "Tumor parts nb" in list(self.json_content['Overall'].keys()) else None
            self.tumor_multifocal_distance = self.json_content['Overall']['Multifocal distance (mm)'] if "Multifocal distance (mm)" in list(self.json_content['Overall'].keys()) else None

            self.statistics = {}
            self.statistics['Main'] = {}
            self.statistics['Main']['Overall'] = TumorStatistics()
            self.statistics['Main']['CoM'] = TumorStatistics()

            # self.statistics['Main']['CoM'].laterality = self.json_content['Main']['CenterOfMass']['Laterality']
            # self.statistics['Main']['CoM'].laterality_percentage = self.json_content['Main']['CenterOfMass']['Laterality_perc']
            # lobes_overlap = {item[0]: item[1] for item in self.json_content['Main']['CenterOfMass']['Lobe']}
            # lobes_overlap_o = collections.OrderedDict(sorted(lobes_overlap.items(), key=operator.itemgetter(1), reverse=True))
            # self.statistics['Main']['CoM'].mni_space_lobes_overlap = lobes_overlap_o

            self.statistics['Main']['Overall'].original_space_tumor_volume = self.json_content['Main']['Total']['Volume original (ml)']
            self.statistics['Main']['Overall'].mni_space_tumor_volume = self.json_content['Main']['Total']['Volume in MNI (ml)']
            self.statistics['Main']['Overall'].left_laterality_percentage = self.json_content['Main']['Total']['Left laterality (%)']
            self.statistics['Main']['Overall'].right_laterality_percentage = self.json_content['Main']['Total']['Right laterality (%)']
            self.statistics['Main']['Overall'].laterality_midline_crossing = self.json_content['Main']['Total']['Midline crossing']

            if self.tumor_type == 'Glioblastoma':
                self.statistics['Main']['Overall'].mni_space_expected_residual_tumor_volume = self.json_content['Main']['Total']['ExpectedResidualVolume (ml)']
                self.statistics['Main']['Overall'].mni_space_resectability_index = self.json_content['Main']['Total']['ResectionIndex']

            # @TODO. Have to fix it based on the actual format, see end of page
            for a in self.json_content['Main']['Total']['CorticalStructures'].keys():
                structures_overlap_o = collections.OrderedDict(sorted(self.json_content['Main']['Total']['CorticalStructures'][a].items(), key=operator.itemgetter(1), reverse=True))
                self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap[a] = structures_overlap_o

            for a in self.json_content['Main']['Total']['SubcorticalStructures'].keys():
                structures_overlap_o = collections.OrderedDict(sorted(self.json_content['Main']['Total']['SubcorticalStructures'][a]['Overlap'].items(), key=operator.itemgetter(1), reverse=True))
                self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap[a] = structures_overlap_o
                structures_distance_o = collections.OrderedDict(sorted(self.json_content['Main']['Total']['SubcorticalStructures'][a]['Distance'].items(), key=operator.itemgetter(1), reverse=False))
                self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance[a] = structures_distance_o

            # tracts_overlap = {item[0]: item[1] for item in self.json_content['Main']['Total']['Tract']['Overlap']}
            # tracts_overlap_o = collections.OrderedDict(sorted(tracts_overlap.items(), key=operator.itemgetter(1), reverse=True))
            # self.statistics['Main']['Overall'].mni_space_tracts_overlap = tracts_overlap_o
            #
            # tracts_dist = {item[0]: item[1] for item in self.json_content['Main']['Total']['Tract']['Distance']}
            # tracts_dist_o = collections.OrderedDict(sorted(tracts_dist.items(), key=operator.itemgetter(1), reverse=False))
            # self.statistics['Main']['Overall'].mni_space_tracts_distance = tracts_dist_o

            # if self.tumor_multifocal:
            #     for p in range(self.tumor_parts):
            #         pname = str(p + 1)
            #         self.statistics[pname] = {}
            #         self.statistics[pname]['Overall'] = TumorStatistics()
            #         self.statistics[pname]['CoM'] = TumorStatistics()
            #
            #         self.statistics[pname]['Overall'].laterality = self.json_content[pname]['Total']['Laterality']
            #         self.statistics[pname]['Overall'].laterality_percentage = self.json_content[pname]['Total']['Laterality_perc']
            #         self.statistics[pname]['Overall'].mni_space_tumor_volume = self.json_content[pname]['Total']['Volume']
            #         self.statistics[pname]['Overall'].mni_space_resectability_score = self.json_content[pname]['Total']['Resectability']
            #
            #         lobes_overlap = {item[0]: item[1] for item in self.json_content[pname]['Total']['Lobe']}
            #         lobes_overlap_o = collections.OrderedDict(
            #             sorted(lobes_overlap.items(), key=operator.itemgetter(1), reverse=True))
            #         self.statistics[pname]['Overall'].mni_space_lobes_overlap = lobes_overlap_o
            #
            #         tracts_overlap = {item[0]: item[1] for item in self.json_content[pname]['Total']['Tract']['Overlap']}
            #         tracts_overlap_o = collections.OrderedDict(
            #             sorted(tracts_overlap.items(), key=operator.itemgetter(1), reverse=True))
            #         self.statistics[pname]['Overall'].mni_space_tracts_overlap = tracts_overlap_o
            #
            #         tracts_dist = {item[0]: item[1] for item in self.json_content[pname]['Total']['Tract']['Distance']}
            #         tracts_dist_o = collections.OrderedDict(
            #             sorted(tracts_dist.items(), key=operator.itemgetter(1), reverse=False))
            #         self.statistics[pname]['Overall'].mni_space_tracts_distance = tracts_dist_o
        except Exception as e:
            logging.warning("Issue encountered when parsing the json file containing the clinical report.")
            logging.warning(traceback.format_exc())


class TumorStatistics():
    def __init__(self):
        self.left_laterality_percentage = None
        self.right_laterality_percentage = None
        self.laterality_midline_crossing = None
        self.original_space_tumor_volume = None
        self.mni_space_tumor_volume = None
        self.mni_space_expected_resectable_tumor_volume = None
        self.mni_space_expected_residual_tumor_volume = None
        self.mni_space_resectability_index = None
        self.mni_space_cortical_structures_overlap = {}
        self.mni_space_subcortical_structures_overlap = {}
        self.mni_space_subcortical_structures_distance = {}
