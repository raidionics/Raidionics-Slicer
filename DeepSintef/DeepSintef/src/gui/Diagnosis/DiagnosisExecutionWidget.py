from __main__ import qt, ctk, slicer, vtk
from glob import glob
import os
import json
from collections import OrderedDict
import subprocess
from copy import deepcopy

from src.utils.resources import SharedResources
from src.DeepSintefLogic import DeepSintefLogic


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
        self.execution_area_groupbox.setTitle("Diagnosis execution")
        self.base_layout.addWidget(self.execution_area_groupbox)
        self.execution_area_layout = qt.QGridLayout(self.execution_area_groupbox)
        self.run_model_pushbutton = qt.QPushButton('Run diagnosis')
        self.execution_area_layout.addWidget(self.run_model_pushbutton, 0, 0)
        self.cancel_model_run_pushbutton = qt.QPushButton('Cancel...')
        self.execution_area_layout.addWidget(self.cancel_model_run_pushbutton, 0, 1)

        self.execution_progress_label = qt.QLabel('Progress:')
        self.execution_area_layout.addWidget(self.execution_progress_label, 1, 0)
        self.execution_progress_textedit = qt.QTextEdit()
        self.execution_progress_textedit.setReadOnly(True)
        self.execution_area_layout.addWidget(self.execution_progress_textedit, 1, 1)
        self.generate_segments_pushbutton = qt.QPushButton('Generate segments')
        self.execution_area_layout.addWidget(self.generate_segments_pushbutton, 2, 0)
        self.generate_segments_pushbutton.setEnabled(False)
        self.optimal_display_pushbutton = qt.QPushButton('Optimal display')
        self.execution_area_layout.addWidget(self.optimal_display_pushbutton, 2, 1)
        self.optimal_display_pushbutton.setEnabled(False)

        self.set_default_execution_area()

    def setup_connections(self):
        pass

    def set_default_execution_area(self):
        self.run_model_pushbutton.setEnabled(False)
        self.run_model_pushbutton.setText('Run diagnosis')
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
        self.run_model_pushbutton.setText('Diagnosing...')
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