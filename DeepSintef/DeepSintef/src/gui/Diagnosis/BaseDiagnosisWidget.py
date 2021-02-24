from __main__ import qt, ctk, slicer, vtk

from src.gui.Diagnosis.DiagnosisInterfaceWidget import *


class BaseDiagnosisWidget(qt.QTabWidget):
    """
    Main GUI object, similar to a QMainWindow, where all widgets and user interactions are defined.
    """
    def __init__(self, parent=None):
        super(BaseDiagnosisWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.diagnosis_interface_widget = DiagnosisInterfaceWidget(parent=self)
        self.base_layout.addWidget(self.diagnosis_interface_widget)
        # self.main_scrollarea = qt.QScrollArea(parent.widget()) # @TODO. How to add the scroll area?
        self.setLayout(self.base_layout)
        self.setup_connections()

    def reload(self):
        print('Reloading the widget diagnosis!!!!!')

    def setup_connections(self):
        pass

    def on_checked(self, val):
        print('something for {}'.format(val))