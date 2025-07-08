from __main__ import qt, ctk, slicer, vtk

from src.RaidionicsLogic import RaidionicsLogic
from src.utils.resources import SharedResources
from src.gui.Diagnosis.DiagnosisInterfaceWidget import *
from src.gui.Diagnosis.DiagnosisExecutionWidget import *
from src.gui.Diagnosis.DiagnosisNeuroResultsWidget import *
from src.gui.Diagnosis.DiagnosisMediastinumResultsWidget import *
from src.logic.neuro_diagnosis_slicer_interface import *
from src.logic.mediastinum_diagnosis_slicer_interface import *


class MyDialog(qt.QDialog):

    def __init__(self, parent=None):
        super(qt.QDialog, self).__init__(parent)
        self.base_layout = qt.QGridLayout()
        self.select_tumor_type_label = qt.QLabel('Tumor type')
        self.base_layout.addWidget(self.select_tumor_type_label, 0, 0)
        self.select_tumor_type_combobox = qt.QComboBox()
        self.select_tumor_type_combobox.addItems(["High-Grade Glioma", "Low-Grade Glioma", "Meningioma", "Metastasis"])
        SharedResources.getInstance().user_diagnosis_configuration['Neuro']['tumor_type'] = "High-Grade Glioma"
        self.base_layout.addWidget(self.select_tumor_type_combobox, 0, 1)
        self.exit_accept_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Ok)
        self.base_layout.addWidget(self.exit_accept_pushbutton, 1, 0)
        self.exit_cancel_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Cancel)
        self.base_layout.addWidget(self.exit_cancel_pushbutton, 1, 1)
        # self.base_layout = qt.QVBoxLayout()
        # self.exit_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel)
        # self.exit_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Ok)
        # self.base_layout.addWidget(self.exit_pushbutton)
        self.setLayout(self.base_layout)

        self.select_tumor_type_combobox.currentTextChanged.connect(self.on_type_selected)
        self.exit_accept_pushbutton.accepted.connect(self.accept)
        self.exit_cancel_pushbutton.rejected.connect(self.reject)

    def on_type_selected(self, text):
        SharedResources.getInstance().user_diagnosis_configuration['Neuro']['tumor_type'] = text


class BaseDiagnosisWidget(qt.QTabWidget):
    """
    Main GUI object, for the diagnosis task.
    """
    def __init__(self, parent=None):
        # @TODO. The current widget should have a scrollable area for slightly better display
        super(BaseDiagnosisWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.diagnosis_interface_widget = DiagnosisInterfaceWidget()
        self.base_layout.addWidget(self.diagnosis_interface_widget)
        self.diagnosis_execution_widget = DiagnosisExecutionWidget()
        self.base_layout.addWidget(self.diagnosis_execution_widget)

        self.diagnosis_results_stackedwidget = qt.QStackedWidget()
        self.diagnosis_results_stackedwidget.setVisible(True)
        self.diagnosis_results_neuro_widget = DiagnosisNeuroResultsWidget()
        self.diagnosis_results_stackedwidget.addWidget(self.diagnosis_results_neuro_widget)
        self.diagnosis_results_mediastinum_widget = DiagnosisMediastinumResultsWidget()
        self.diagnosis_results_stackedwidget.addWidget(self.diagnosis_results_mediastinum_widget)
        self.base_layout.addWidget(self.diagnosis_results_stackedwidget)
        # self.base_layout.addStretch(1)

        self.setLayout(self.base_layout)
        self.setup_connections()

    def set_default(self):
        if SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'neuro_diagnosis':
            NeuroDiagnosisSlicerInterface.getInstance().set_default()
        elif SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'mediastinum_diagnosis':
            MediastinumDiagnosisSlicerInterface.getInstance().set_default()

    def reload(self):
        # @TODO. Which clean-up/reload here?
        pass

    def setup_connections(self):
        self.diagnosis_execution_widget.run_model_pushbutton.connect("clicked()", self.on_run_diagnosis)
        self.diagnosis_execution_widget.cancel_model_run_pushbutton.connect("clicked()", self.on_cancel_diagnosis_run)
        self.diagnosis_execution_widget.generate_segments_pushbutton.connect("clicked()", self.on_generate_segments)
        self.diagnosis_execution_widget.optimal_display_pushbutton.connect("clicked()", self.on_optimal_display)

        self.diagnosis_interface_widget.diagnosis_available_signal.connect(self.diagnosis_execution_widget.on_diagnosis_available)

    def update_results_area(self):
        if SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'neuro_diagnosis':
            #@TODO. Should collapse everything except the results box, for better viewing?
            self.diagnosis_results_stackedwidget.setCurrentWidget(self.diagnosis_results_neuro_widget)
            self.diagnosis_results_neuro_widget.update_results()
        elif SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'mediastinum_diagnosis':
            self.diagnosis_results_stackedwidget.setCurrentWidget(self.diagnosis_results_mediastinum_widget)
            self.diagnosis_results_mediastinum_widget.update_results()
        self.diagnosis_results_stackedwidget.setVisible(True)

    def on_run_diagnosis(self):
        RaidionicsLogic.getInstance().logic_task = 'reporting'
        if self.diagnosis_interface_widget.diagnosis_model_parameters.json_dict['organ'] == 'Brain':
            # User input needed to select the correct brain tumor type in order to use the corresponding model
            diag = MyDialog(self)
            diag.exec()
        RaidionicsLogic.getInstance().run(self.diagnosis_interface_widget.diagnosis_model_parameters)

    def on_cancel_diagnosis_run(self):
        RaidionicsLogic.getInstance().cancel_run()
        self.diagnosis_execution_widget.generate_segments_pushbutton.setEnabled(False)

    def on_generate_segments(self):
        # @TODO. Indication that the generation is ongoing, can take 30sec...
        self.diagnosis_execution_widget.generate_segments_pushbutton.setEnabled(False)
        if SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'neuro_diagnosis':
            NeuroDiagnosisSlicerInterface.getInstance().generate_segmentations_from_labelmaps(self.diagnosis_interface_widget.diagnosis_model_parameters)
        elif SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'mediastinum_diagnosis':
            MediastinumDiagnosisSlicerInterface.getInstance().generate_segmentations_from_labelmaps(self.diagnosis_interface_widget.diagnosis_model_parameters)
        else:
            pass
        self.diagnosis_execution_widget.optimal_display_pushbutton.setEnabled(True)

    def on_checked(self, val):
        print('something for {}'.format(val))

    def on_logic_event_start(self):
        self.diagnosis_execution_widget.on_logic_event_start()
        if SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'neuro_diagnosis':
            self.diagnosis_results_neuro_widget.on_logic_event_start()
        else:
            pass

    #@TODO. Should there be a logic_event_abort to not update results/etc... if the run has been prematurely stopped.
    def on_logic_event_end(self):
        self.diagnosis_execution_widget.on_logic_event_end()
        if SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'neuro_diagnosis':
            self.diagnosis_results_neuro_widget.on_logic_event_end()
        else:
            pass
        self.update_results_area()

    def on_logic_event_progress(self, progress, log):
        self.diagnosis_execution_widget.on_logic_event_progress(progress, log)

    def on_optimal_display(self):
        """
        """
        if SharedResources.getInstance().user_diagnosis_configuration['Default']['task'] == 'neuro_diagnosis':
            NeuroDiagnosisSlicerInterface.getInstance().on_optimal_display(
                self.diagnosis_interface_widget.diagnosis_model_parameters)
        else:
            pass
        return
