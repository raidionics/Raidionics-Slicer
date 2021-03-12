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
from src.gui.Diagnosis.DiagnosisNeuroPartResultsWidget import *


class DiagnosisNeuroResultsWidget(qt.QWidget):
    """
    GUI component displaying the diagnosis results when applied to a neuro case.
    """
    def __init__(self, parent=None):
        super(DiagnosisNeuroResultsWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.setup_results_area()
        self.setLayout(self.base_layout)

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

        self.overall_results_area_tabwidget = qt.QTabWidget()
        self.results_groupbox_scrollarea.setWidget(self.overall_results_area_tabwidget)
        self.__setup_overall_results_area()
        self.results_widgets = {}

    def __setup_overall_results_area(self):
        self.overall_results_base_dummywidget = qt.QWidget()
        self.overall_results_base_layout = qt.QGridLayout()
        self.overall_results_base_dummywidget.setLayout(self.overall_results_base_layout)
        self.overall_results_area_tabwidget.addTab(self.overall_results_base_dummywidget, 'General')

        self.results_overall_tumor_found_label = qt.QLabel('Tumor found:')
        self.results_overall_tumor_found_lineedit = qt.QLineEdit()
        self.results_overall_tumor_found_lineedit.setReadOnly(True)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_found_label, 0, 0)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_found_lineedit, 0, 1)

        self.results_overall_tumor_type_label = qt.QLabel('Tumor type:')
        self.results_overall_tumor_type_lineedit = qt.QLineEdit()
        self.results_overall_tumor_type_lineedit.setReadOnly(True)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_type_label, 1, 0)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_type_lineedit, 1, 1)

        self.results_overall_tumor_multifocal_label = qt.QLabel('Mutifocal:')
        self.results_overall_tumor_mutifocal_lineedit = qt.QLineEdit()
        self.results_overall_tumor_mutifocal_lineedit.setReadOnly(True)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_multifocal_label, 2, 0)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_mutifocal_lineedit, 2, 1)

    def __clean_results_area(self):
        for i, wid in enumerate(self.results_widgets.keys()):
            self.results_widgets[wid].setParent(None)
            del self.results_widgets[wid]

        self.results_widgets = {}
        w = DiagnosisNeuroPartResultsWidget(parent=self)
        self.overall_results_area_tabwidget.addTab(w, 'Main')
        self.results_widgets['Main'] = w

    def __setup_tumor_parts_results_area(self, nb_parts):
        for i in range(nb_parts):
            w = DiagnosisNeuroPartResultsWidget(parent=self)
            self.overall_results_area_tabwidget.addTab(w, 'Part ' + str(i+1))
            self.results_widgets[str(i+1)] = w

    def update_results(self):
        diagnosis_file = os.path.join(SharedResources.getInstance().output_path, 'Diagnosis.json')
        NeuroDiagnosisParameters.getInstance().from_json(diagnosis_file)

        self.__clean_results_area()
        if NeuroDiagnosisParameters.getInstance().tumor_multifocal:
            self.__setup_tumor_parts_results_area(nb_parts=NeuroDiagnosisParameters.getInstance().tumor_parts)

        self.__update_results_gui()

    def __update_results_gui(self):
        self.results_overall_tumor_found_lineedit.setText(NeuroDiagnosisParameters.getInstance().tumor_presence_state)
        self.results_overall_tumor_type_lineedit.setText(NeuroDiagnosisParameters.getInstance().tumor_type)
        self.results_overall_tumor_mutifocal_lineedit.setText(NeuroDiagnosisParameters.getInstance().tumor_multifocal)

        for i, wid in enumerate(self.results_widgets.keys()):
            self.results_widgets[wid].update_results(NeuroDiagnosisParameters.getInstance().statistics[wid])
