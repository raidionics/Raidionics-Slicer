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
        self.run_model_pushbutton = qt.QPushButton('Run diagnosis')
        self.base_layout.addWidget(self.run_model_pushbutton)
        self.cancel_model_run_pushbutton = qt.QPushButton('Cancel...')
        self.base_layout.addWidget(self.cancel_model_run_pushbutton)

        self.generate_segments_pushbutton = qt.QPushButton('Generate segments')
        self.base_layout.addWidget(self.generate_segments_pushbutton)
        self.generate_segments_pushbutton.setEnabled(False)

        self.set_default_execution_area()

    def setup_connections(self):
        pass

    def set_default_execution_area(self):
        self.run_model_pushbutton.setEnabled(True)
        self.run_model_pushbutton.setText('Run diagnosis')
        self.cancel_model_run_pushbutton.setEnabled(False)

    def set_default_interactive_area(self):
        pass

    def on_logic_event_start(self):
        self.run_model_pushbutton.setEnabled(False)
        self.run_model_pushbutton.setText('Diagnosing...')
        self.cancel_model_run_pushbutton.setEnabled(True)
        self.generate_segments_pushbutton.setEnabled(True)

    def on_logic_event_end(self):
        self.set_default_execution_area()
