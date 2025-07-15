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
        self.tumor_type = None
        self.volumes = {}
        self.structure_features = {}

    def from_json(self, filename):
        try:
            self.clear()
            with open(filename, 'r') as pfile:
                self.json_content = json.load(pfile)

            self.structure_features = {}
            for s in self.json_content.keys():
                self.structure_features[s] = {}
                for space in self.json_content[s].keys():
                    curr_features = StructureFeatures()
                    curr_features.init_from_json(self.json_content[s][space])
                    if curr_features.type:
                        self.tumor_type = curr_features.type
                    self.structure_features[s][space] = curr_features
        except Exception as e:
            logging.warning("Issue encountered when parsing the json file containing the clinical report.")
            logging.warning(traceback.format_exc())


class StructureFeatures():
    def __init__(self):
        self.type = None
        self.volume = None
        self.diameters_shortaxis = None
        self.diameters_longaxis = None
        self.diameters_feret = None
        self.diameters_equivalent = None
        self.location_left_laterality = None
        self.location_right_laterality = None
        self.location_midline_crossing = None
        self.multifocality_elements = None
        self.multifocality_max_distance = None
        self.multifocality_status = None
        self.resectability_index = None
        self.resectability_residual = None
        self.resectability_resectable = None
        self.cortical_structures_overlap = {}
        self.subcortical_structures_overlap = {}
        self.subcortical_structures_distance = {}

    def init_from_json(self, json_dict):
        if "Type" in json_dict.keys():
            self.type = json_dict["Type"]
        if "Volume (ml)" in json_dict.keys():
            self.volume = json_dict["Volume (ml)"]
        if "Diameters" in json_dict.keys():
            if "Short-axis diameter (mm)" in json_dict["Diameters"].keys():
                self.diameters_shortaxis = json_dict["Diameters"]["Short-axis diameter (mm)"]
            if "Long-axis diameter (mm)" in json_dict["Diameters"].keys():
                self.diameters_longaxis = json_dict["Diameters"]["Long-axis diameter (mm)"]
            if "Feret diameter (mm)" in json_dict["Diameters"].keys():
                self.diameters_feret = json_dict["Diameters"]["Feret diameter (mm)"]
            if "Equivalent diameter area (mm)" in json_dict["Diameters"].keys():
                self.diameters_equivalent = json_dict["Diameters"]["Equivalent diameter area (mm)"]
        if "Location" in json_dict.keys():
            if "Left laterality (%)" in json_dict["Location"].keys():
                self.location_left_laterality = json_dict["Location"]["Left laterality (%)"]
            if "Right laterality (%)" in json_dict["Location"].keys():
                self.location_right_laterality = json_dict["Location"]["Right laterality (%)"]
            if "Midline crossing" in json_dict["Location"].keys():
                self.location_midline_crossing = json_dict["Location"]["Midline crossing"]
        if "Multifocality" in json_dict.keys():
            if "Elements" in json_dict["Multifocality"].keys():
                self.multifocality_elements = json_dict["Multifocality"]["Elements"]
            if "Max distance (mm)" in json_dict["Multifocality"].keys():
                self.multifocality_max_distance = json_dict["Multifocality"]["Max distance (mm)"]
            if "Status" in json_dict["Multifocality"].keys():
                self.multifocality_status = json_dict["Multifocality"]["Status"]
        if "Resectability" in json_dict.keys():
            if "Index" in json_dict["Resectability"].keys():
                self.resectability_index = json_dict["Resectability"]["Index"]
            if "Resectable volume (ml)" in json_dict["Resectability"].keys():
                self.resectability_resectable = json_dict["Resectability"]["Resectable volume (ml)"]
            if "Expected residual volume (ml)" in json_dict["Resectability"].keys():
                self.resectability_residual = json_dict["Resectability"]["Expected residual volume (ml)"]
        if "Cortical Profile" in json_dict.keys():
            for atlas in json_dict["Cortical Profile"].keys():
                self.cortical_structures_overlap[atlas] = dict(
                    sorted(json_dict["Cortical Profile"][atlas]["Overlap"].items(), key=lambda item: item[1],
                           reverse=True))
        if "Subcortical Profile" in json_dict.keys():
            for atlas in json_dict["Subcortical Profile"].keys():
                self.subcortical_structures_distance[atlas] = dict(
                    sorted(json_dict["Subcortical Profile"][atlas]["Distance"].items(), key=lambda item: item[1],
                           reverse=False))
                self.subcortical_structures_overlap[atlas] = dict(
                    sorted(json_dict["Subcortical Profile"][atlas]["Overlap"].items(), key=lambda item: item[1],
                           reverse=True))