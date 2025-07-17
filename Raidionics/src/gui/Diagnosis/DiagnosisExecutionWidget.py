from __main__ import qt, ctk, slicer, vtk
from glob import glob
import os
import json
from collections import OrderedDict
import subprocess
from copy import deepcopy

from src.utils.resources import SharedResources
from src.RaidionicsLogic import RaidionicsLogic


class DiagnosisExecutionWidget(qt.QWidget):
    """
    GUI component enabling to run a diagnosis and interact with the results.
    """
    def __init__(self, parent=None):
        super(DiagnosisExecutionWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.setup_execution_area()
        self.setLayout(self.base_layout)
        self.setup_connections()

    def setup_execution_area(self):
        self.execution_area_groupbox = ctk.ctkCollapsibleGroupBox()
        self.execution_area_groupbox.setTitle("RADS execution")
        self.base_layout.addWidget(self.execution_area_groupbox)
        self.execution_area_layout = qt.QGridLayout(self.execution_area_groupbox)
        self.run_model_pushbutton = qt.QPushButton('Run RADS')
        self.execution_area_layout.addWidget(self.run_model_pushbutton, 0, 0)
        self.cancel_model_run_pushbutton = qt.QPushButton('Cancel...')
        self.execution_area_layout.addWidget(self.cancel_model_run_pushbutton, 0, 1)

        self.advanced_options_groupbox = ctk.ctkCollapsibleGroupBox()
        self.advanced_options_groupbox.setTitle("Advanced options")
        # self.advanced_options_groupbox.setCheckable(False)
        tmp_layout = qt.QGridLayout()
        self.advanced_inputs_header_label = qt.QLabel('Inputs: ')
        self.advanced_use_stripped_inputs_label = qt.QLabel('Stripped')
        self.advanced_use_stripped_inputs_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_inputs_header_label, 0, 0)
        tmp_layout.addWidget(self.advanced_use_stripped_inputs_label, 0, 1)
        tmp_layout.addWidget(self.advanced_use_stripped_inputs_checkbox, 0, 2)
        self.advanced_use_registered_inputs_label = qt.QLabel('Registered')
        self.advanced_use_registered_inputs_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_use_registered_inputs_label, 0, 3)
        tmp_layout.addWidget(self.advanced_use_registered_inputs_checkbox, 0, 4)
        self.advanced_report_cortical_structures_header_label = qt.QLabel('Cortical: ')
        self.advanced_report_mni_atlas_label = qt.QLabel('MNI')
        self.advanced_report_mni_atlas_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_report_cortical_structures_header_label, 1, 0)
        tmp_layout.addWidget(self.advanced_report_mni_atlas_label, 1, 1)
        tmp_layout.addWidget(self.advanced_report_mni_atlas_checkbox, 1, 2)
        self.advanced_report_sc7_atlas_label = qt.QLabel('Schaefer7')
        self.advanced_report_sc7_atlas_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_report_sc7_atlas_label, 1, 3)
        tmp_layout.addWidget(self.advanced_report_sc7_atlas_checkbox, 1, 4)
        self.advanced_report_sc17_atlas_label = qt.QLabel('Schaefer17')
        self.advanced_report_sc17_atlas_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_report_sc17_atlas_label, 1, 5)
        tmp_layout.addWidget(self.advanced_report_sc17_atlas_checkbox, 1, 6)
        self.advanced_report_ho_atlas_label = qt.QLabel('Harvard-Oxford')
        self.advanced_report_ho_atlas_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_report_ho_atlas_label, 1, 7)
        tmp_layout.addWidget(self.advanced_report_ho_atlas_checkbox, 1, 8)
        self.advanced_options_groupbox.setLayout(tmp_layout)
        self.advanced_report_subcortical_structures_header_label = qt.QLabel('Subcortical: ')
        self.advanced_report_bcb_atlas_label = qt.QLabel('BCB')
        self.advanced_report_bcb_atlas_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_report_subcortical_structures_header_label, 2, 0)
        tmp_layout.addWidget(self.advanced_report_bcb_atlas_label, 2, 1)
        tmp_layout.addWidget(self.advanced_report_bcb_atlas_checkbox, 2, 2)
        self.advanced_options_groupbox.setLayout(tmp_layout)
        self.advanced_report_braingrid_wm_atlas_label = qt.QLabel('BrainGrid')
        self.advanced_report_braingrid_wm_atlas_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_report_braingrid_wm_atlas_label, 2, 3)
        tmp_layout.addWidget(self.advanced_report_braingrid_wm_atlas_checkbox, 2, 4)
        self.advanced_options_groupbox.setLayout(tmp_layout)
        self.execution_area_layout.addWidget(self.advanced_options_groupbox, 1, 0, 1, 2)

        self.execution_progress_label = qt.QLabel('Progress:')
        self.execution_area_layout.addWidget(self.execution_progress_label, 2, 0)
        self.execution_progress_textedit = qt.QTextEdit()
        self.execution_progress_textedit.setReadOnly(True)
        self.execution_area_layout.addWidget(self.execution_progress_textedit, 2, 1)
        self.generate_segments_pushbutton = qt.QPushButton('Generate segments')
        self.execution_area_layout.addWidget(self.generate_segments_pushbutton, 3, 0)
        self.generate_segments_pushbutton.setEnabled(False)
        self.optimal_display_pushbutton = qt.QPushButton('Optimal display')
        self.execution_area_layout.addWidget(self.optimal_display_pushbutton, 3, 1)
        self.optimal_display_pushbutton.setEnabled(False)

        self.set_default_execution_area()

    def setup_connections(self):
        self.advanced_use_stripped_inputs_checkbox.connect("stateChanged(int)", self.on_use_stripped_inputs_change)
        self.advanced_use_registered_inputs_checkbox.connect("stateChanged(int)", self.on_use_registered_inputs_change)
        self.advanced_report_mni_atlas_checkbox.connect("stateChanged(int)", self.on_report_mni_atlas_change)
        self.advanced_report_sc7_atlas_checkbox.connect("stateChanged(int)", self.on_report_sc7_atlas_change)
        self.advanced_report_sc17_atlas_checkbox.connect("stateChanged(int)", self.on_report_sc17_atlas_change)
        self.advanced_report_ho_atlas_checkbox.connect("stateChanged(int)", self.on_report_ho_atlas_change)
        self.advanced_report_bcb_atlas_checkbox.connect("stateChanged(int)", self.on_report_bcb_atlas_change)
        self.advanced_report_braingrid_wm_atlas_checkbox.connect("stateChanged(int)", self.on_report_braingrid_wm_atlas_change)

    def set_default_execution_area(self):
        self.run_model_pushbutton.setEnabled(False)
        self.run_model_pushbutton.setText('Run RADS')
        self.cancel_model_run_pushbutton.setEnabled(False)

    def set_default_interactive_area(self):
        pass

    def on_diagnosis_available(self, state):
        if state:
            self.run_model_pushbutton.setEnabled(True)
        else:
            self.run_model_pushbutton.setEnabled(False)

    def on_logic_event_start(self):
        self.run_model_pushbutton.setEnabled(False)
        self.run_model_pushbutton.setText('RADS processing...')
        self.cancel_model_run_pushbutton.setEnabled(True)
        self.generate_segments_pushbutton.setEnabled(False)

    def on_logic_event_end(self):
        self.set_default_execution_area()
        self.run_model_pushbutton.setEnabled(True)
        self.generate_segments_pushbutton.setEnabled(True)

    def on_logic_event_progress(self, progress, log):
        # @TODO. Should the number of steps be known beforehand (in the json) to indicate 1/5, 2/5, etc...
        # @TODO. Should a timer be used to indicate elapsed time for each task?
        if 'SLICERLOG' in log:
            task = log.split(':')[1].split('-')[0].strip()
            status = log.split(':')[1].split('-')[1].strip()
            log_text = self.execution_progress_textedit.plainText
            new_log_text = ''
            if status == 'Begin':
                new_log_text = str(log_text) + task + ': ...'
            elif status == 'End':
                new_log_text = str(log_text)[:-3] + 'Done' + '\n'

            self.execution_progress_textedit.setText(new_log_text)
            self.execution_progress_textedit.moveCursor(qt.QTextCursor.End)
            # self.execution_progress_textedit.append(log)

    def on_use_stripped_inputs_change(self, state):
        if state == qt.Qt.Checked:
            SharedResources.getInstance().user_configuration['Runtime']['use_stripped_data'] = 'True'
        elif state == qt.Qt.Unchecked:
            SharedResources.getInstance().user_configuration['Runtime']['use_stripped_data'] = 'False'

    def on_use_registered_inputs_change(self, state):
        if state == qt.Qt.Checked:
            SharedResources.getInstance().user_configuration['Runtime']['use_registered_data'] = 'True'
        elif state == qt.Qt.Unchecked:
            SharedResources.getInstance().user_configuration['Runtime']['use_registered_data'] = 'False'

    def on_report_mni_atlas_change(self, state):
        pl = SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'].split(',') if SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] != "" else []
        if state == qt.Qt.Checked:
            if "MNI" not in pl:
                pl.append("MNI")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] = ','.join(pl)
        elif state == qt.Qt.Unchecked:
            if "MNI" in pl:
                pl.remove("MNI")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] = ','.join(pl)

    def on_report_sc7_atlas_change(self, state):
        pl = SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'].split(',') if SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] != "" else []
        if state == qt.Qt.Checked:
            if "Schaefer7" not in pl:
                pl.append("Schaefer7")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] = ','.join(pl)
        elif state == qt.Qt.Unchecked:
            if "Schaefer7" in pl:
                pl.remove("Schaefer7")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] = ','.join(pl)

    def on_report_sc17_atlas_change(self, state):
        pl = SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'].split(',') if SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] != "" else []
        if state == qt.Qt.Checked:
            if "Schaefer17" not in pl:
                pl.append("Schaefer17")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] = ','.join(pl)
        elif state == qt.Qt.Unchecked:
            if "Schaefer17" in pl:
                pl.remove("Schaefer17")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] = ','.join(pl)

    def on_report_ho_atlas_change(self, state):
        pl = SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'].split(',') if SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] != "" else []
        if state == qt.Qt.Checked:
            if "Harvard-Oxford" not in pl:
                pl.append("Harvard-Oxford")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] = ','.join(pl)
        elif state == qt.Qt.Unchecked:
            if "Harvard-Oxford" in pl:
                pl.remove("Harvard-Oxford")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['cortical_features'] = ','.join(pl)

    def on_report_bcb_atlas_change(self, state):
        pl = SharedResources.getInstance().user_diagnosis_configuration['Neuro']['subcortical_features'].split(',') if SharedResources.getInstance().user_diagnosis_configuration['Neuro']['subcortical_features'] != "" else []
        if state == qt.Qt.Checked:
            if "BCB" not in pl:
                pl.append("BCB")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['subcortical_features'] = ','.join(pl)
        elif state == qt.Qt.Unchecked:
            if "BCB" in pl:
                pl.remove("BCB")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['subcortical_features'] = ','.join(pl)

    def on_report_braingrid_wm_atlas_change(self, state):
        pl = SharedResources.getInstance().user_diagnosis_configuration['Neuro']['subcortical_features'].split(',') if SharedResources.getInstance().user_diagnosis_configuration['Neuro']['subcortical_features'] != "" else []
        if state == qt.Qt.Checked:
            if "BrainGrid" not in pl:
                pl.append("BrainGrid")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['subcortical_features'] = ','.join(pl)
        elif state == qt.Qt.Unchecked:
            if "BrainGrid" in pl:
                pl.remove("BrainGrid")
                SharedResources.getInstance().user_diagnosis_configuration['Neuro']['subcortical_features'] = ','.join(pl)
