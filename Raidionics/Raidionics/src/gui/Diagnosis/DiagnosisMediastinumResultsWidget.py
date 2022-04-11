from __main__ import qt, ctk, slicer, vtk
from glob import glob
import os
import json
from collections import OrderedDict
import subprocess

from src.utils.resources import SharedResources
from src.logic.model_parameters import *
from src.RaidionicsLogic import RaidionicsLogic
from src.logic.mediastinum_diagnosis_result_parameters import *
# from src.gui.Diagnosis.DiagnosisMediastinumPartResultsWidget import *


class DiagnosisMediastinumResultsWidget(qt.QWidget):
    """
    GUI component displaying the diagnosis results when applied to a mediastinum case.
    """
    def __init__(self, parent=None):
        super(DiagnosisMediastinumResultsWidget, self).__init__(parent)
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

        self.results_overall_lymphnodes_count_label = qt.QLabel('Lymph nodes:')
        self.results_overall_lymphnodes_count_lineedit = qt.QLineEdit()
        self.results_overall_lymphnodes_count_lineedit.setReadOnly(True)
        self.overall_results_base_layout.addWidget(self.results_overall_lymphnodes_count_label, 1, 0)
        self.overall_results_base_layout.addWidget(self.results_overall_lymphnodes_count_lineedit, 1, 1)

        self.results_overall_lymphnodes_malignant_count_label = qt.QLabel('Lymph nodes (malignant):')
        self.results_overall_lymphnodes_malignant_count_lineedit = qt.QLineEdit()
        self.results_overall_lymphnodes_malignant_count_lineedit.setReadOnly(True)
        self.overall_results_base_layout.addWidget(self.results_overall_lymphnodes_malignant_count_label, 2, 0)
        self.overall_results_base_layout.addWidget(self.results_overall_lymphnodes_malignant_count_lineedit, 2, 1)

    def __clean_results_area(self):
        for i, wid in enumerate(self.results_widgets.keys()):
            self.results_widgets[wid].setParent(None)
            del self.results_widgets[wid]

        self.results_widgets = {}

    def update_results(self):
        diagnosis_file = os.path.join(SharedResources.getInstance().output_path, 'Diagnosis.json')
        MediastinumDiagnosisParameters.getInstance().from_json(diagnosis_file)

        self.__clean_results_area()
        self.__update_results_gui()

    def __update_results_gui(self):
        self.results_overall_lymphnodes_count_lineedit.setText(MediastinumDiagnosisParameters.getInstance().lymphnodes_count)

        w = qt.QTableWidget()
        w.setColumnCount(4)
        w.setRowCount(MediastinumDiagnosisParameters.getInstance().lymphnodes_count)
        for l in range(MediastinumDiagnosisParameters.getInstance().lymphnodes_count):
            ln_stats = MediastinumDiagnosisParameters.getInstance().statistics['LymphNodes'][str(l + 1)]
            w.setItem(l, 0, qt.QTableWidgetItem(str(l+1)))
            w.setItem(l, 1, qt.QTableWidgetItem(str(ln_stats.volume)))
            w.setItem(l, 2, qt.QTableWidgetItem(str(ln_stats.axis_diameters[0])))
            w.setItem(l, 3, qt.QTableWidgetItem(str(ln_stats.axis_diameters[1])))
        w.setHorizontalHeaderLabels(['Index', 'Volume', 'Long-axis', 'Short-axis'])
        self.overall_results_area_tabwidget.addTab(w, 'Lymph-Nodes')
        self.results_widgets['Lymph-Nodes'] = w
