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
        self.model_execution_area_groupbox = ctk.ctkCollapsibleGroupBox()
        self.model_execution_area_groupbox.setTitle("Model execution")
        self.base_layout.addWidget(self.model_execution_area_groupbox)
        # Layout within the dummy collapsible button
        self.model_execution_area_layout = qt.QGridLayout(self.model_execution_area_groupbox)

        self.run_model_pushbutton = qt.QPushButton('Run segmentation')
        self.cancel_model_run_pushbutton = qt.QPushButton('Cancel...')
        self.model_execution_area_layout.addWidget(self.run_model_pushbutton, 0, 0)
        self.model_execution_area_layout.addWidget(self.cancel_model_run_pushbutton, 0, 1)

        self.model_execution_progress_label = qt.QLabel('Progress:')
        self.model_execution_area_layout.addWidget(self.model_execution_progress_label, 1, 0)
        self.model_execution_progress_textedit = qt.QTextEdit()
        self.model_execution_progress_textedit.setReadOnly(True)
        self.model_execution_area_layout.addWidget(self.model_execution_progress_textedit, 1, 1)

        self.advanced_options_groupbox = qt.QGroupBox("Advanced options")
        self.advanced_options_groupbox.setCheckable(False)
        tmp_layout = qt.QGridLayout()
        self.advanced_use_gpu_label = qt.QLabel('Use GPU')
        self.advanced_use_gpu_checkbox = qt.QCheckBox()
        tmp_layout.addWidget(self.advanced_use_gpu_label, 0, 0)
        tmp_layout.addWidget(self.advanced_use_gpu_checkbox, 0, 1)
        self.advanced_predictions_type_label = qt.QLabel('Predictions')
        self.advanced_predictions_type_combobox = qt.QComboBox()
        self.advanced_predictions_type_combobox.addItems(['Probabilities', 'Binary'])
        tmp_layout.addWidget(self.advanced_predictions_type_label, 1, 0)
        tmp_layout.addWidget(self.advanced_predictions_type_combobox, 1, 1)
        self.advanced_resampling_label = qt.QLabel('Resampling')
        self.advanced_resampling_combobox = qt.QComboBox()
        self.advanced_resampling_combobox.addItems(['First', 'Second'])
        tmp_layout.addWidget(self.advanced_resampling_label, 1, 2)
        tmp_layout.addWidget(self.advanced_resampling_combobox, 1, 3)
        self.advanced_options_groupbox.setLayout(tmp_layout)
        self.model_execution_area_layout.addWidget(self.advanced_options_groupbox, 2, 0, 1, 2)

        self.set_default_execution_area()

    def setup_interactive_results_area(self):
        self.interactive_options_area_groupbox = ctk.ctkCollapsibleGroupBox()
        self.interactive_options_area_groupbox.setTitle("Interactive options")
        self.base_layout.addWidget(self.interactive_options_area_groupbox)
        self.interactive_area_layout = qt.QGridLayout(self.interactive_options_area_groupbox)


        # self.interactive_options_groupbox = qt.QGroupBox("Interactive options")
        # self.interactive_options_groupbox.setCheckable(False)
        # tmp_layout = qt.QGridLayout()

        self.interactive_thresholding_combobox = qt.QComboBox()
        self.interactive_thresholding_slider = qt.QSlider(qt.Qt.Horizontal)
        self.interactive_thresholding_slider.setMaximum(100)
        self.interactive_thresholding_slider.setMinimum(1)
        self.interactive_thresholding_slider.setSingleStep(1)
        self.interactive_area_layout.addWidget(self.interactive_thresholding_combobox, 0, 0)
        self.interactive_area_layout.addWidget(self.interactive_thresholding_slider, 0, 1)
        self.interactive_current_threshold_label = qt.QLabel('Threshold')
        self.interactive_current_threshold_spinbox = qt.QSpinBox()
        self.interactive_current_threshold_spinbox.setSingleStep(1)
        self.interactive_current_threshold_spinbox.setMinimum(1)
        self.interactive_current_threshold_spinbox.setMaximum(100)
        self.interactive_current_threshold_spinbox.setEnabled(False)
        self.interactive_optimal_thr_pushbutton = qt.QPushButton('Recommended')
        self.interactive_optimal_thr_pushbutton.setToolTip('Use the recommended threshold value.')
        self.interactive_area_layout.addWidget(self.interactive_current_threshold_label, 1, 0)
        self.interactive_area_layout.addWidget(self.interactive_current_threshold_spinbox, 1, 1)
        self.interactive_area_layout.addWidget(self.interactive_optimal_thr_pushbutton, 1, 2)

        self.interactive_thresholding_slider.setEnabled(False)
        self.interactive_optimal_thr_pushbutton.setEnabled(False)
        self.interactive_options_area_groupbox.setChecked(False)
        # self.interactive_options_groupbox.setLayout(tmp_layout)
        # self.base_layout.addWidget(self.interactive_options_groupbox)

        self.set_default_interactive_area()

    def setup_connections(self):
        self.advanced_use_gpu_checkbox.connect("stateChanged(int)", self.on_use_gpu_change)
        self.advanced_resampling_combobox.connect("currentIndexChanged(QString)", self.on_sampling_strategy_change)
        self.advanced_predictions_type_combobox.connect("currentIndexChanged(QString)", self.on_predictions_type_change)

        # self.interactive_thresholding_slider.valueChanged.connect(self.on_interactive_slider_moved)

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
            SharedResources.getInstance().use_gpu = True
        elif state == qt.Qt.Unchecked:
            SharedResources.getInstance().use_gpu = False

    def on_sampling_strategy_change(self, order):
        if order == 'First':
            SharedResources.getInstance().user_configuration['Predictions']['reconstruction_order'] = 'resample_first'
        else:
            SharedResources.getInstance().user_configuration['Predictions']['reconstruction_order'] = 'resample_second'

    def on_predictions_type_change(self, type):
        if type == 'Binary':
            SharedResources.getInstance().user_configuration['Predictions']['reconstruction_method'] = 'thresholding'
        else:
            SharedResources.getInstance().user_configuration['Predictions']['reconstruction_method'] = 'probabilities'

    def on_logic_event_start(self):
        self.run_model_pushbutton.setEnabled(False)
        self.run_model_pushbutton.setText('Segmenting...')
        self.cancel_model_run_pushbutton.setEnabled(True)
        self.model_execution_progress_textedit.setPlainText('')
        self.advanced_use_gpu_checkbox.setEnabled(False)
        self.advanced_resampling_combobox.setEnabled(False)
        self.advanced_predictions_type_combobox.setEnabled(False)

    def on_logic_event_end(self):
        self.set_default_execution_area()
        self.interactive_thresholding_slider.setEnabled(True)
        self.interactive_optimal_thr_pushbutton.setEnabled(True)
        self.interactive_options_area_groupbox.setChecked(True)

    def on_logic_event_progress(self, progress, log):
        # Should the number of steps be known beforehand (in the json) to indicate 1/5, 2/5, etc...
        # Should a timer be used to indicate elapsed time for each task?
        # The QTextEdit should automatically scroll to bottom also to follow the latest status...
        if 'SLICERLOG' in log:
            task = log.split(':')[1].split('-')[0].strip()
            status = log.split(':')[1].split('-')[1].strip()
            log_text = self.model_execution_progress_textedit.plainText
            new_log_text = ''
            if status == 'Begin':
                new_log_text = str(log_text) + task + ': ...'
            elif status == 'End':
                new_log_text = str(log_text)[:-3] + 'Done' + '\n'

            self.model_execution_progress_textedit.setText(new_log_text)

    #@TODO. to finish
    def populate_interactive_label_classes(self, classes):
        for c, class_name in enumerate(classes): #self.modelParameters.outputs.keys()
            self.interactive_thresholding_combobox.addItem(class_name)

    def on_interactive_slider_moved(self, value, model_parameters):
        # @TODO. Should save the current value for each class in order to redisplay the correct value upon re-selection from the combobox
        current_class = self.interactive_thresholding_combobox.currentText
        value = float(value)
        original_data = deepcopy(DeepSintefLogic.getInstance().output_raw_values[current_class])
        volume_node = slicer.util.getNode(model_parameters.outputs[current_class].GetName())
        arr = slicer.util.arrayFromVolume(volume_node)
        # Increase image contrast
        #arr[:] = original_data
        arr[original_data < (value/100)] = 0
        arr[original_data >= (value/100)] = 1
        slicer.util.arrayFromVolumeModified(volume_node)
        self.interactive_current_threshold_spinbox.setValue(value)
        # DeepSintefLogic.getInstance().current_class_thresholds[self.runtimeParametersThresholdClassCombobox.currentIndex] = value
        # self.interactive_current_threshold_lineedit.setText(str(value))

    def on_interactive_best_threshold_clicked(self, model_parameters):
        current_class = self.interactive_thresholding_combobox.currentText

        # The value is supposed to be coming from the slider, which ranges [1, 100], hence the multiplication
        optimal_threshold = float(str(model_parameters.iodict[current_class]['threshold'])) * 100.
        self.interactive_thresholding_slider.setValue(optimal_threshold)
        #self.on_interactive_slider_moved(optimal_threshold, model_parameters)
