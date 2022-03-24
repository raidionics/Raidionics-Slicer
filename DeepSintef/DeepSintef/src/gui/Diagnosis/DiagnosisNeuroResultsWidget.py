from __main__ import qt, ctk, slicer, vtk
from glob import glob
import os
import json
from collections import OrderedDict
import subprocess
import shutil

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
        self.__setup_connections()
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
        self.overall_results_base_layout = qt.QVBoxLayout()
        self.overall_results_base_dummywidget.setLayout(self.overall_results_base_layout)
        self.overall_results_area_tabwidget.addTab(self.overall_results_base_dummywidget, 'General')

        self.results_status_groupbox = ctk.ctkCollapsibleGroupBox()
        self.results_status_groupbox.setTitle("Status")
        self.results_status_groupbox_layout = qt.QVBoxLayout()
        self.results_overall_tumor_found_layout = qt.QHBoxLayout()
        self.results_overall_tumor_found_label = qt.QLabel('Tumor found:')
        self.results_overall_tumor_found_lineedit = qt.QLineEdit()
        self.results_overall_tumor_found_lineedit.setReadOnly(True)
        self.results_overall_tumor_found_layout.addWidget(self.results_overall_tumor_found_label)
        self.results_overall_tumor_found_layout.addWidget(self.results_overall_tumor_found_lineedit)
        self.results_status_groupbox_layout.addLayout(self.results_overall_tumor_found_layout)

        self.results_overall_tumor_type_layout = qt.QHBoxLayout()
        self.results_overall_tumor_type_label = qt.QLabel('Tumor type:')
        self.results_overall_tumor_type_lineedit = qt.QLineEdit()
        self.results_overall_tumor_type_lineedit.setReadOnly(True)
        self.results_overall_tumor_type_layout.addWidget(self.results_overall_tumor_type_label)
        self.results_overall_tumor_type_layout.addWidget(self.results_overall_tumor_type_lineedit)
        self.results_status_groupbox_layout.addLayout(self.results_overall_tumor_type_layout)

        self.results_overall_tumor_multifocal_layout = qt.QHBoxLayout()
        self.results_overall_tumor_multifocal_label = qt.QLabel('Mutifocality:')
        self.results_overall_tumor_mutifocal_lineedit = qt.QLineEdit()
        self.results_overall_tumor_mutifocal_lineedit.setReadOnly(True)
        self.results_overall_tumor_multifocal_layout.addWidget(self.results_overall_tumor_multifocal_label)
        self.results_overall_tumor_multifocal_layout.addWidget(self.results_overall_tumor_mutifocal_lineedit)
        self.results_status_groupbox_layout.addLayout(self.results_overall_tumor_multifocal_layout)
        self.results_status_groupbox_layout.addStretch(1)

        self.results_status_groupbox.setLayout(self.results_status_groupbox_layout)
        self.overall_results_base_layout.addWidget(self.results_status_groupbox)

        self.results_overall_tumor_multifocality_groupbox = ctk.ctkCollapsibleGroupBox()
        self.results_overall_tumor_multifocality_groupbox.setTitle('Multifocality')
        self.results_overall_tumor_multifocality_layout = qt.QGridLayout()
        self.results_overall_tumor_multifocal_pieces_label = qt.QLabel('Number of focis:')
        self.results_overall_tumor_mutifocal_pieces_lineedit = qt.QLineEdit()
        self.results_overall_tumor_mutifocal_pieces_lineedit.setReadOnly(True)
        self.results_overall_tumor_multifocal_distance_label = qt.QLabel('Maximum distance between foci (mm):')
        self.results_overall_tumor_mutifocal_distance_lineedit = qt.QLineEdit()
        self.results_overall_tumor_mutifocal_distance_lineedit.setReadOnly(True)
        self.results_overall_tumor_multifocality_layout.addWidget(self.results_overall_tumor_multifocal_pieces_label, 0, 0)
        self.results_overall_tumor_multifocality_layout.addWidget(self.results_overall_tumor_mutifocal_pieces_lineedit, 0, 1)
        self.results_overall_tumor_multifocality_layout.addWidget(self.results_overall_tumor_multifocal_distance_label, 1, 0)
        self.results_overall_tumor_multifocality_layout.addWidget(self.results_overall_tumor_mutifocal_distance_lineedit, 1, 1)
        self.results_overall_tumor_multifocality_groupbox.setLayout(self.results_overall_tumor_multifocality_layout)
        self.overall_results_base_layout.addWidget(self.results_overall_tumor_multifocality_groupbox)

        self.results_export_groupbox = ctk.ctkCollapsibleGroupBox()
        self.results_export_groupbox.setTitle("Export")
        self.results_export_groupbox_layout = qt.QVBoxLayout()
        self.results_export_pushbutton = qt.QPushButton('Export report')
        self.results_export_groupbox_layout.addWidget(self.results_export_pushbutton)
        self.results_export_groupbox_layout.addStretch(1)
        self.results_export_groupbox.setLayout(self.results_export_groupbox_layout)
        self.overall_results_base_layout.addWidget(self.results_export_groupbox)
        self.overall_results_base_layout.addStretch(1)

    def __setup_connections(self):
        self.results_export_pushbutton.clicked.connect(self.__on_export_clicked)

    def on_logic_event_start(self):
        self.__clean_results_area()

    def on_logic_event_end(self):
        pass

    def __on_export_clicked(self):
        filepath = qt.QFileDialog.getSaveFileName(self, self.tr("Save standardized report"),
                                                  os.path.expanduser('~'), self.tr("Report files (*.txt *.csv *.json)"))
        extension = filepath.split('.')[-1]
        if os.path.exists(os.path.join(SharedResources.getInstance().output_path, 'Diagnosis.' + extension)):
            shutil.copy(src=os.path.join(SharedResources.getInstance().output_path, 'Diagnosis.' + extension),
                        dst=filepath)

    def __clean_results_area(self):
        for i in reversed(range(len(self.results_widgets))):
            # Should have index+1, assuming 'Overall' is at position 0 all the time
            self.overall_results_area_tabwidget.removeTab(i+1)

        self.results_widgets = {}
        w = DiagnosisNeuroPartResultsWidget(parent=self)
        self.overall_results_area_tabwidget.addTab(w, 'Full extent')
        self.results_widgets['Main'] = w

    def __setup_tumor_parts_results_area(self, nb_parts):
        for i in range(nb_parts):
            w = DiagnosisNeuroPartResultsWidget(parent=self)
            self.overall_results_area_tabwidget.addTab(w, 'Foci ' + str(i+1))
            self.results_widgets[str(i+1)] = w

    def update_results(self):
        diagnosis_file = os.path.join(SharedResources.getInstance().output_path, 'Diagnosis.json')
        NeuroDiagnosisParameters.getInstance().from_json(diagnosis_file)

        self.__clean_results_area()
        if NeuroDiagnosisParameters.getInstance().tumor_multifocal:
            self.__setup_tumor_parts_results_area(nb_parts=NeuroDiagnosisParameters.getInstance().tumor_parts)

        self.__update_results_gui()
        self.results_collapsible_groupbox.setCollapsed(True)

    def __update_results_gui(self):
        self.results_overall_tumor_found_lineedit.setText(NeuroDiagnosisParameters.getInstance().tumor_presence_state)
        self.results_overall_tumor_type_lineedit.setText(NeuroDiagnosisParameters.getInstance().tumor_type)
        multifocality_text = "Yes" if NeuroDiagnosisParameters.getInstance().tumor_multifocal else "No"
        self.results_overall_tumor_mutifocal_lineedit.setText(multifocality_text)
        self.results_overall_tumor_mutifocal_pieces_lineedit.setText(NeuroDiagnosisParameters.getInstance().tumor_parts)
        self.results_overall_tumor_mutifocal_distance_lineedit.setText(str(NeuroDiagnosisParameters.getInstance().tumor_multifocal_distance) + " mm")

        if NeuroDiagnosisParameters.getInstance().tumor_parts > 1:
            self.results_overall_tumor_multifocality_groupbox.setVisible(True)
        else:
            self.results_overall_tumor_multifocality_groupbox.setVisible(False)

        for i, wid in enumerate(self.results_widgets.keys()):
            self.results_widgets[wid].update_results(NeuroDiagnosisParameters.getInstance().statistics[wid])
