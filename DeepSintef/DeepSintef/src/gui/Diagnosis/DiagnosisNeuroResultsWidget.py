from __main__ import qt, ctk, slicer, vtk
from glob import glob
import os
import json
from collections import OrderedDict
import subprocess

from src.utils.resources import SharedResources
from src.logic.model_parameters import *
from src.DeepSintefLogic import DeepSintefLogic
from src.logic.neuro_diagnosis_result_parameters import *


class DiagnosisNeuroResultsWidget(qt.QWidget):
    """
    GUI component displaying the diagnosis results when applied to a neuro case.
    """
    def __init__(self, parent=None):
        super(DiagnosisNeuroResultsWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.setup_results_area()
        self.setLayout(self.base_layout)
        # self.results = NeuroDiagnosisParameters()

    def setup_results_area(self):
        # Setting up the CtkCollapsible and inner scrollable widgets/layouts
        self.results_collapsible_groupbox = ctk.ctkCollapsibleGroupBox()
        self.results_collapsible_groupbox.setTitle("Diagnosis results")
        self.base_layout.addWidget(self.results_collapsible_groupbox)

        self.results_scrollarea_layout = qt.QHBoxLayout(self.results_collapsible_groupbox)
        self.results_groupbox_scrollarea = qt.QScrollArea()
        self.results_groupbox_scrollarea.setVerticalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOn)
        self.results_groupbox_scrollarea.setHorizontalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)
        self.results_groupbox_scrollarea.setWidgetResizable(True)
        self.results_scrollarea_layout.addWidget(self.results_groupbox_scrollarea)
        self.results_dummy_widget = qt.QWidget()
        self.results_groupbox_scrollarea.setWidget(self.results_dummy_widget)
        self.results_base_layout = qt.QGridLayout()
        self.results_dummy_widget.setLayout(self.results_base_layout)

        self.results_overall_tumor_volume_label = qt.QLabel('Overall tumor volume:')
        self.results_overall_tumor_volume_lineedit = qt.QLineEdit()
        self.results_overall_tumor_volume_lineedit.setReadOnly(True)
        self.results_base_layout.addWidget(self.results_overall_tumor_volume_label, 0, 0)
        self.results_base_layout.addWidget(self.results_overall_tumor_volume_lineedit, 0, 1)

    def update_results(self):
        diagnosis_file = os.path.join(SharedResources.getInstance().output_path, 'Diagnosis.json')
        NeuroDiagnosisParameters.getInstance().from_json(diagnosis_file)
        self.results_overall_tumor_volume_lineedit.setText(NeuroDiagnosisParameters.getInstance().statistics['Main']['Overall'].mni_space_tumor_volume)