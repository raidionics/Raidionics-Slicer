from __main__ import qt, ctk, slicer, vtk

from src.DeepSintefLogic import DeepSintefLogic
from src.gui.Diagnosis.DiagnosisInterfaceWidget import *
from src.gui.Diagnosis.DiagnosisExecutionWidget import *


class BaseDiagnosisWidget(qt.QTabWidget):
    """
    Main GUI object, similar to a QMainWindow, where all widgets and user interactions are defined.
    """
    def __init__(self, parent=None):
        super(BaseDiagnosisWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.diagnosis_interface_widget = DiagnosisInterfaceWidget(parent=self)
        self.base_layout.addWidget(self.diagnosis_interface_widget)
        self.diagnosis_execution_widget = DiagnosisExecutionWidget(parent=self)
        self.base_layout.addWidget(self.diagnosis_execution_widget)
        # self.main_scrollarea = qt.QScrollArea(parent.widget()) # @TODO. How to add the scroll area?
        self.setLayout(self.base_layout)
        self.setup_connections()

    def reload(self):
        print('Reloading the widget diagnosis!!!!!')

    def setup_connections(self):
        self.diagnosis_execution_widget.run_model_pushbutton.connect("clicked()", self.on_run_diagnosis)
        self.diagnosis_execution_widget.cancel_model_run_pushbutton.connect("clicked()", self.on_cancel_diagnosis_run)
        self.diagnosis_execution_widget.generate_segments_pushbutton.connect("clicked()", self.on_generate_segments)

    def on_run_diagnosis(self):
        DeepSintefLogic.getInstance().logic_task = 'diagnosis'
        DeepSintefLogic.getInstance().run(self.diagnosis_interface_widget.diagnosis_model_parameters)

    def on_cancel_diagnosis_run(self):
        DeepSintefLogic.getInstance().cancel_run()

    def on_generate_segments(self):
        DeepSintefLogic.getInstance().generate_segmentations_from_labelmaps(self.diagnosis_interface_widget.diagnosis_model_parameters)

    def on_checked(self, val):
        print('something for {}'.format(val))

    def on_logic_event_start(self):
        self.diagnosis_execution_widget.on_logic_event_start()

    def on_logic_event_end(self):
        self.diagnosis_execution_widget.on_logic_event_end()
