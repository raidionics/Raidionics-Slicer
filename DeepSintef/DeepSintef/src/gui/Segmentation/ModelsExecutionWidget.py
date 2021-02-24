from __main__ import qt, ctk, slicer, vtk
from glob import glob
import os
import json
from collections import OrderedDict
import subprocess
from copy import deepcopy

from src.utils.resources import SharedResources
from src.DeepSintefLogic import DeepSintefLogic


class ModelsExecutionWidget(qt.QWidget):
    """
    GUI component enabling to run a model and interact with the results.
    """
    def __init__(self, parent=None):
        super(ModelsExecutionWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.setup_execution_area()
        self.setup_interactive_results_area()
        self.setLayout(self.base_layout)
        self.setup_connections()

    def setup_execution_area(self):
        self.run_model_pushbutton = qt.QPushButton('Run segmentation')
        self.cancel_model_run_pushbutton = qt.QPushButton('Cancel...')
        self.base_layout.addWidget(self.run_model_pushbutton)
        self.base_layout.addWidget(self.cancel_model_run_pushbutton)

        self.advanced_options_groupbox = qt.QGroupBox("Advanced options")
        self.advanced_options_groupbox.setCheckable(False)
        tmp_layout = qt.QGridLayout()
        self.advanced_use_gpu_label = qt.QLabel('Use GPU')
        self.advanced_use_gpu_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_use_gpu_label, 0, 0)
        tmp_layout.addWidget(self.advanced_use_gpu_checkbox, 0, 1)
        self.advanced_predictions_type_label = qt.QLabel('Predictions')
        self.advanced_predictions_type_combobox = qt.QComboBox()
        self.advanced_predictions_type_combobox.addItems(['Binary', 'Probabilities'])
        tmp_layout.addWidget(self.advanced_predictions_type_label, 1, 0)
        tmp_layout.addWidget(self.advanced_predictions_type_combobox, 1, 1)
        self.advanced_resampling_label = qt.QLabel('Resampling')
        self.advanced_resampling_combobox = qt.QComboBox()
        self.advanced_resampling_combobox.addItems(['First', 'Second'])
        tmp_layout.addWidget(self.advanced_resampling_label, 1, 2)
        tmp_layout.addWidget(self.advanced_resampling_combobox, 1, 3)
        self.advanced_options_groupbox.setLayout(tmp_layout)
        self.base_layout.addWidget(self.advanced_options_groupbox)

        self.set_default_execution_area()

    def setup_interactive_results_area(self):
        self.interactive_options_groupbox = qt.QGroupBox("Interactive options")
        self.interactive_options_groupbox.setCheckable(False)
        tmp_layout = qt.QGridLayout()

        self.interactive_thresholding_slider = qt.QSlider(qt.Qt.Horizontal)
        self.interactive_thresholding_slider.setMaximum(100)
        self.interactive_thresholding_slider.setMinimum(0)
        self.interactive_thresholding_slider.setSingleStep(5)
        tmp_layout.addWidget(self.interactive_thresholding_slider, 0, 0)
        self.interactive_current_threshold_label = qt.QLabel('Threshold')
        self.interactive_current_threshold_lineedit = qt.QLineEdit()
        self.interactive_current_threshold_lineedit.setValidator(qt.QIntValidator())
        tmp_layout.addWidget(self.interactive_current_threshold_label, 1, 0)
        tmp_layout.addWidget(self.interactive_current_threshold_lineedit, 1, 1)

        self.interactive_options_groupbox.setLayout(tmp_layout)
        self.base_layout.addWidget(self.interactive_options_groupbox)

        self.set_default_interactive_area()

    def setup_connections(self):
        self.advanced_use_gpu_checkbox.connect("stateChanged(int)", self.on_use_gpu_change)
        self.advanced_resampling_combobox.connect("currentIndexChanged(QString)", self.on_sampling_strategy_change)
        self.advanced_predictions_type_combobox.connect("currentIndexChanged(QString)", self.on_predictions_type_change)

        self.interactive_thresholding_slider.valueChanged.connect(self.on_interactive_slider_moved)

    def set_default_execution_area(self):
        self.run_model_pushbutton.setEnabled(True)
        self.run_model_pushbutton.setText('Run segmentation')
        self.cancel_model_run_pushbutton.setEnabled(False)

        self.advanced_use_gpu_checkbox.setEnabled(True)
        self.advanced_resampling_combobox.setEnabled(True)
        self.advanced_predictions_type_combobox.setEnabled(True)

    def set_default_interactive_area(self):
        pass

    def on_use_gpu_change(self, state):
        if state == qt.Qt.Checked:
            DeepSintefLogic.getInstance().use_gpu = True
        elif state == qt.Qt.Unchecked:
            DeepSintefLogic.getInstance().use_gpu = False

    def on_sampling_strategy_change(self, order):
        if order == 'First':
            DeepSintefLogic.getInstance().user_configuration['Predictions']['reconstruction_order'] = 'resample_first'
        else:
            DeepSintefLogic.getInstance().user_configuration['Predictions']['reconstruction_order'] = 'resample_second'

    def on_predictions_type_change(self, type):
        if type == 'Binary':
            DeepSintefLogic.getInstance().user_configuration['Predictions']['reconstruction_method'] = 'thresholding'
        else:
            DeepSintefLogic.getInstance().user_configuration['Predictions']['reconstruction_method'] = 'probabilities'

    def on_logic_event_start(self):
        self.run_model_pushbutton.setEnabled(False)
        self.run_model_pushbutton.setText('Segmenting...')
        self.cancel_model_run_pushbutton.setEnabled(True)
        self.advanced_use_gpu_checkbox.setEnabled(False)
        self.advanced_resampling_combobox.setEnabled(False)
        self.advanced_predictions_type_combobox.setEnabled(False)

    def on_logic_event_end(self):
        self.set_default_execution_area()

    #@TODO. to finish
    def populate_interactive_label_classes(self, classes):
        for c, class_name in enumerate(classes): #self.modelParameters.outputs.keys()
            self.runtimeParametersThresholdClassCombobox.addItem(class_name)

    def on_interactive_slider_moved(self, value):
        current_class = self.runtimeParametersThresholdClassCombobox.currentText  # 'OutputLabel'
        value = float(value)
        original_data = deepcopy(DeepSintefLogic.getInstance().output_raw_values[current_class])
        volume_node = slicer.util.getNode(self.modelParameters.outputs[current_class].GetName())
        arr = slicer.util.arrayFromVolume(volume_node)
        # Increase image contrast
        #arr[:] = original_data
        arr[original_data < (value/100)] = 0
        arr[original_data >= (value/100)] = 1
        slicer.util.arrayFromVolumeModified(volume_node)
        DeepSintefLogic.getInstance().current_class_thresholds[self.runtimeParametersThresholdClassCombobox.currentIndex] = value
        self.interactive_current_threshold_lineedit.setText(str(value))
