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
        # self.results_dummy_widget = qt.QWidget()
        # self.results_groupbox_scrollarea.setWidget(self.results_dummy_widget)
        # self.results_base_layout = qt.QGridLayout()
        # self.results_dummy_widget.setLayout(self.results_base_layout)

        self.overall_results_area_tabwidget = qt.QTabWidget()
        self.results_groupbox_scrollarea.setWidget(self.overall_results_area_tabwidget)
        self.__setup_overall_results_area()
        self.__setup_main_tumor_results_area()
        self.__setup_tumor_parts_results_area()

    def __setup_overall_results_area(self):
        self.overall_results_base_dummywidget = qt.QWidget()
        self.overall_results_base_layout = qt.QGridLayout()
        self.overall_results_base_dummywidget.setLayout(self.overall_results_base_layout)
        self.overall_results_area_tabwidget.addTab(self.overall_results_base_dummywidget, 'General')

        self.results_overall_tumor_type_label = qt.QLabel('Tumor type:')
        self.results_overall_tumor_type_lineedit = qt.QLineEdit()
        self.results_overall_tumor_type_lineedit.setReadOnly(True)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_type_label, 0, 0)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_type_lineedit, 0, 1)

        self.results_overall_tumor_multifocal_label = qt.QLabel('Mutifocal:')
        self.results_overall_tumor_mutifocal_lineedit = qt.QLineEdit()
        self.results_overall_tumor_mutifocal_lineedit.setReadOnly(True)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_multifocal_label, 1, 0)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_mutifocal_lineedit, 1, 1)

    def __setup_main_tumor_results_area(self):
        self.main_tumor_results_base_dummywidget = qt.QWidget()
        self.main_tumor_results_base_layout = qt.QGridLayout()
        self.main_tumor_results_base_dummywidget.setLayout(self.main_tumor_results_base_layout)
        self.overall_results_area_tabwidget.addTab(self.main_tumor_results_base_dummywidget, 'Main')

        self.results_main_tumor_volume_label = qt.QLabel('Volume:')
        self.results_main_tumor_volume_lineedit = qt.QLineEdit()
        self.results_main_tumor_volume_lineedit.setReadOnly(True)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_volume_label, 0, 0)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_volume_lineedit, 0, 1)

        self.results_main_tumor_laterality_label = qt.QLabel('Laterality:')
        self.results_main_tumor_laterality_lineedit = qt.QLineEdit()
        self.results_main_tumor_laterality_lineedit.setReadOnly(True)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_laterality_label, 1, 0)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_laterality_lineedit, 1, 1)

        self.results_main_tumor_lobes_label = qt.QLabel('Lobes:')
        self.results_main_tumor_lobes_tablewidget = qt.QTableWidget()
        self.results_main_tumor_lobes_tablewidget.setColumnCount(2)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_lobes_label, 2, 0)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_lobes_tablewidget, 2, 1)

        self.results_main_tumor_tracts_overlap_label = qt.QLabel('Tracts overlap:')
        self.results_main_tumor_tracts_overlap_tablewidget = qt.QTableWidget()
        self.results_main_tumor_tracts_overlap_tablewidget.setColumnCount(2)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_tracts_overlap_label, 3, 0)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_tracts_overlap_tablewidget, 3, 1)

        self.results_main_tumor_tracts_distance_label = qt.QLabel('Tracts distance:')
        self.results_main_tumor_tracts_distance_tablewidget = qt.QTableWidget()
        self.results_main_tumor_tracts_distance_tablewidget.setColumnCount(2)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_tracts_distance_label, 4, 0)
        self.main_tumor_results_base_layout.addWidget(self.results_main_tumor_tracts_distance_tablewidget, 4, 1)

    def __setup_tumor_parts_results_area(self):
        self.tumor_parts_results_base_dummywidget = qt.QWidget()
        self.tumor_parts_results_base_layout = qt.QGridLayout()
        self.tumor_parts_results_base_dummywidget.setLayout(self.tumor_parts_results_base_layout)
        self.overall_results_area_tabwidget.addTab(self.tumor_parts_results_base_dummywidget, 'Parts')

    def update_results(self):
        diagnosis_file = os.path.join(SharedResources.getInstance().output_path, 'Diagnosis.json')
        NeuroDiagnosisParameters.getInstance().from_json(diagnosis_file)
        self.__update_results_gui()

    def __update_results_gui(self):
        #@TODO. Should start by running a clean method to remove previous displayed results?
        self.results_overall_tumor_type_lineedit.setText(NeuroDiagnosisParameters.getInstance().tumor_type)
        self.results_overall_tumor_mutifocal_lineedit.setText(NeuroDiagnosisParameters.getInstance().tumor_multifocal)

        self.results_main_tumor_volume_lineedit.setText(str(NeuroDiagnosisParameters.getInstance().statistics['Main']['Overall'].mni_space_tumor_volume) + 'ml')
        self.results_main_tumor_laterality_lineedit.setText(NeuroDiagnosisParameters.getInstance().statistics['Main']['Overall'].laterality +
                                                            ' with ' + str(NeuroDiagnosisParameters.getInstance().statistics['Main']['Overall'].laterality_percentage) + '%')
        main_lobes = NeuroDiagnosisParameters.getInstance().statistics['Main']['Overall'].mni_space_lobes_overlap
        self.results_main_tumor_lobes_tablewidget.setRowCount(len(main_lobes.keys()))
        for l, ln in enumerate(main_lobes.keys()):
            self.results_main_tumor_lobes_tablewidget.setItem(l, 0, qt.QTableWidgetItem(ln))
            self.results_main_tumor_lobes_tablewidget.setItem(l, 1, qt.QTableWidgetItem(str(main_lobes[ln]) + '%'))

        tracts_overlap = NeuroDiagnosisParameters.getInstance().statistics['Main']['Overall'].mni_space_tracts_overlap
        self.results_main_tumor_tracts_overlap_tablewidget.setRowCount(len(tracts_overlap.keys()))
        for l, ln in enumerate(tracts_overlap.keys()):
            self.results_main_tumor_tracts_overlap_tablewidget.setItem(l, 0, qt.QTableWidgetItem(ln))
            self.results_main_tumor_tracts_overlap_tablewidget.setItem(l, 1, qt.QTableWidgetItem(str(tracts_overlap[ln]) + '%'))

        tracts_distance = NeuroDiagnosisParameters.getInstance().statistics['Main']['Overall'].mni_space_tracts_distance
        self.results_main_tumor_tracts_distance_tablewidget.setRowCount(len(tracts_distance.keys()))
        for l, ln in enumerate(tracts_distance.keys()):
            self.results_main_tumor_tracts_distance_tablewidget.setItem(l, 0, qt.QTableWidgetItem(ln))
            self.results_main_tumor_tracts_distance_tablewidget.setItem(l, 1, qt.QTableWidgetItem(str(tracts_distance[ln]) + 'mm'))

        self.results_main_tumor_lobes_tablewidget.horizontalHeader().setStretchLastSection(True)
        self.results_main_tumor_lobes_tablewidget.verticalHeader().setStretchLastSection(True)
        self.results_main_tumor_lobes_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
        self.results_main_tumor_lobes_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)

        self.results_main_tumor_tracts_overlap_tablewidget.horizontalHeader().setStretchLastSection(True)
        self.results_main_tumor_tracts_overlap_tablewidget.verticalHeader().setStretchLastSection(True)
        self.results_main_tumor_tracts_overlap_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
        self.results_main_tumor_tracts_overlap_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)

        self.results_main_tumor_tracts_distance_tablewidget.horizontalHeader().setStretchLastSection(True)
        self.results_main_tumor_tracts_distance_tablewidget.verticalHeader().setStretchLastSection(True)
        self.results_main_tumor_tracts_distance_tablewidget.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
        self.results_main_tumor_tracts_distance_tablewidget.verticalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)