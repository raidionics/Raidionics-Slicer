from __main__ import qt, ctk, slicer, vtk

from src.utils.resources import SharedResources
from src.DeepSintefLogic import DeepSintefLogic
from src.gui.Segmentation.ModelsInterfaceWidget import *
from src.gui.Segmentation.ModelsExecutionWidget import *


class BaseSegmentationWidget(qt.QWidget):
    """
    Main GUI object for the segmentation task.
    """
    def __init__(self, parent=None):
        super(BaseSegmentationWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.model_interface_widget = ModelsInterfaceWidget(parent=self)
        self.base_layout.addWidget(self.model_interface_widget)
        self.model_execution_widget = ModelsExecutionWidget(parent=self)
        self.base_layout.addWidget(self.model_execution_widget)
        self.setLayout(self.base_layout)
        self.setup_connections()

    def set_default(self):
        # @TODO. What should the clean-up/reload be?
        pass

    def setup_connections(self):
        self.model_execution_widget.run_model_pushbutton.connect("clicked()", self.on_run_model)
        self.model_execution_widget.cancel_model_run_pushbutton.connect("clicked()", self.on_cancel_model_run)
        self.model_execution_widget.interactive_thresholding_slider.valueChanged.connect(self.on_interactive_slider_moved)
        self.model_execution_widget.interactive_optimal_thr_pushbutton.connect("clicked()", self.on_interactive_best_threshold_clicked)

        self.model_interface_widget.segmentation_available_signal.connect(self.model_execution_widget.on_segmentation_available)

    def on_run_model(self):
        DeepSintefLogic.getInstance().logic_task = 'segmentation'
        DeepSintefLogic.getInstance().run(self.model_interface_widget.model_parameters)
        if SharedResources.getInstance().user_configuration['Predictions']['reconstruction_method'] == 'probabilities':
            self.model_execution_widget.populate_interactive_label_classes(self.model_interface_widget.model_parameters.outputs.keys())
            self.on_interactive_best_threshold_clicked()

    def on_cancel_model_run(self):
        DeepSintefLogic.getInstance().cancel_run()

    def on_logic_event_start(self):
        self.model_execution_widget.on_logic_event_start()

    def on_logic_event_end(self):
        self.model_execution_widget.on_logic_event_end()

    def on_logic_event_progress(self, progress, log):
        self.model_execution_widget.on_logic_event_progress(progress, log)

    def on_interactive_slider_moved(self, value):
        self.model_execution_widget.on_interactive_slider_moved(value, self.model_interface_widget.model_parameters)

    def on_interactive_best_threshold_clicked(self):
        self.model_execution_widget.on_interactive_best_threshold_clicked(self.model_interface_widget.model_parameters)