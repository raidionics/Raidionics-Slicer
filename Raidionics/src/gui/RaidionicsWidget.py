import traceback

from slicer.ScriptedLoadableModule import *
import logging

import json
import platform
import os
import numpy
import re
import subprocess
import shutil
import threading
from collections import OrderedDict
from glob import glob
from time import sleep
from copy import deepcopy
from __main__ import qt, ctk, slicer, vtk

import SimpleITK as sitk
import sitkUtils
from src.RaidionicsLogic import *
from src.gui.Segmentation.BaseSegmentationWidget import BaseSegmentationWidget
from src.gui.Diagnosis.BaseDiagnosisWidget import BaseDiagnosisWidget
from src.utils.resources import SharedResources


class WarningDialog(qt.QDialog):

    def __init__(self, parent=None):
        super(qt.QDialog, self).__init__(parent)
        self.setWindowTitle("Irreversible action.")
        self.base_layout = qt.QGridLayout()
        self.main_label = qt.QLabel()
        self.base_layout.addWidget(self.main_label, 0, 0, 1, 2)
        self.exit_accept_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Ok)
        self.base_layout.addWidget(self.exit_accept_pushbutton, 1, 0)
        self.exit_cancel_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Cancel)
        self.base_layout.addWidget(self.exit_cancel_pushbutton, 1, 1)
        self.setLayout(self.base_layout)
        self.exit_accept_pushbutton.accepted.connect(self.accept)
        self.exit_cancel_pushbutton.rejected.connect(self.reject)

    def setText(self, text):
        self.main_label.setText(text)


class RaidionicsWidget():
    """
    Main GUI object, similar to a QMainWindow, where all widgets and user interactions are defined for the plugin.
    """
    def __init__(self, parent=None):
        """
        By default, only the 'Help & Acknowledgement' tab is created, inherited from the default widget?
        :param parent: the parent will be a reference to the 3D Slicer window where this plugin will be displayed
        """
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.parent.show()

        self.modelParameters = None
        self.logic = None
        shared = SharedResources.getInstance()
        shared.set_environment()

    def setup(self):
        """
        Instantiate the plugin layout and connect widgets
        :return:
        """
        self.__set_interface()
        self.__set_layout_dimensions()
        self.setup_connections()

    def __set_interface(self):
        self.setup_docker_widget()
        self.setup_global_options_widget()
        self.setup_user_interactions_widget()
        self.layout.addStretch(1)

    def setup_docker_widget(self):
        self.dockerGroupBox = ctk.ctkCollapsibleGroupBox()
        self.dockerGroupBox.setTitle('Docker Settings')
        self.dockerGroupBox.setChecked(False)
        self.layout.addWidget(self.dockerGroupBox)
        dockerForm = qt.QFormLayout(self.dockerGroupBox)
        self.dockerPath = ctk.ctkPathLineEdit()
        # self.dockerPath.setMaximumWidth(300)
        dockerForm.addRow("Docker Executable Path:", self.dockerPath)
        self.docker_test_pushbutton = qt.QPushButton('Test!')
        dockerForm.addRow("Test Docker Configuration:", self.docker_test_pushbutton)
        if platform.system() == 'Darwin':
            self.dockerPath.setCurrentPath('/usr/local/bin/docker')
        if platform.system() == 'Linux':
            self.dockerPath.setCurrentPath('/usr/bin/docker')
        if platform.system() == 'Windows':
            self.dockerPath.setCurrentPath("C:/Program Files/Docker/Docker/resources/bin/docker.exe")

        # use nvidia-docker if it is installed, gpu use will be enabled only if the docker image has also been
        # created with gpu support
        nvidiaDockerPath = self.dockerPath.currentPath.replace('bin/docker', 'bin/nvidia-docker')
        if os.path.isfile(nvidiaDockerPath):
            self.dockerPath.setCurrentPath(nvidiaDockerPath)

        SharedResources.getInstance().docker_path = self.dockerPath.currentPath

    def setup_global_options_widget(self):
        self.global_options_groupbox = ctk.ctkCollapsibleGroupBox()
        self.global_options_groupbox.collapsed = True
        self.global_options_groupbox.setTitle("Global options")
        self.layout.addWidget(self.global_options_groupbox)
        # Layout within the dummy collapsible button
        self.global_options_groupbox_layout = qt.QFormLayout(self.global_options_groupbox)
        # option 1: actively updating local models
        self.global_options_active_models_update_checkbox = ctk.ctkCheckBox()
        self.global_options_active_models_update_checkbox.setToolTip("Click to let the system check for possible updates available for the local models.")
        self.global_options_groupbox_layout.addRow("Active model update:", self.global_options_active_models_update_checkbox)
        # option 2: way to clean related Docker images
        self.global_options_purge_docker_images_pushbutton = ctk.ctkPushButton()
        self.global_options_purge_docker_images_pushbutton.setToolTip("Click to purge the computer from old/unused Docker images.")
        self.global_options_groupbox_layout.addRow("Purge Docker images:", self.global_options_purge_docker_images_pushbutton)
        # option 3: way to clean old models
        self.global_options_purge_models_pushbutton = ctk.ctkPushButton()
        self.global_options_purge_models_pushbutton.setToolTip("Click to purge the computer from all existing Raidionics models.")
        self.global_options_groupbox_layout.addRow("Purge Raidionics models:", self.global_options_purge_models_pushbutton)

    def setup_user_interactions_widget(self):
        self.user_interactions_groupbox = ctk.ctkCollapsibleGroupBox()
        self.user_interactions_groupbox.collapsed = False
        self.user_interactions_groupbox.setTitle("Interactive")
        self.user_interactions_groupbox_layout = qt.QVBoxLayout()
        self.tasks_tabwidget = qt.QTabWidget()
        self.base_segmentation_widget = BaseSegmentationWidget(self.parent)
        self.tasks_tabwidget.addTab(self.base_segmentation_widget, 'Segmentation')
        self.base_diagnosis_widget = BaseDiagnosisWidget(self.parent)
        self.tasks_tabwidget.addTab(self.base_diagnosis_widget, 'Reporting (RADS)')
        # self.base_diagnosis_widget.setEnabled(True)
        # self.base_diagnosis_widget.setToolTip("Currently disabled for maintenance, please use Raidionics in the meantime.")
        self.logging_textedit = qt.QTextEdit()
        #self.logging_textedit.setEnabled(False)
        self.logging_textedit.setReadOnly(True)
        self.tasks_tabwidget.addTab(self.logging_textedit, 'Logging')
        self.user_interactions_groupbox_layout.addWidget(self.tasks_tabwidget)
        self.user_interactions_groupbox.setLayout(self.user_interactions_groupbox_layout)
        self.layout.addWidget(self.user_interactions_groupbox)

        # self.tasks_tabwidget = qt.QTabWidget()
        # self.base_segmentation_widget = BaseSegmentationWidget(self.parent)
        # self.tasks_tabwidget.addTab(self.base_segmentation_widget, 'Segmentation')
        # self.base_diagnosis_widget = BaseDiagnosisWidget(self.parent)
        # self.tasks_tabwidget.addTab(self.base_diagnosis_widget, 'Diagnosis')
        # self.logging_textedit = qt.QTextEdit()
        # #self.logging_textedit.setEnabled(False)
        # self.logging_textedit.setReadOnly(True)
        # self.tasks_tabwidget.addTab(self.logging_textedit, 'Logging')
        # self.layout.addWidget(self.tasks_tabwidget)

    def __set_layout_dimensions(self):
        self.global_options_purge_docker_images_pushbutton.setMinimumHeight(22)
        self.global_options_purge_docker_images_pushbutton.setMaximumHeight(28)
        self.global_options_purge_docker_images_pushbutton.setMaximumWidth(400)
        self.global_options_purge_models_pushbutton.setMinimumHeight(22)
        self.global_options_purge_models_pushbutton.setMaximumHeight(28)
        self.global_options_purge_models_pushbutton.setMaximumWidth(400)

    def setup_connections(self):
        self.docker_test_pushbutton.connect('clicked(bool)', self.on_test_docker_button_pressed)
        self.tasks_tabwidget.connect('currentChanged(int)', self.on_task_tabwidget_tabchanged)
        self.global_options_active_models_update_checkbox.stateChanged.connect(self.on_models_active_update_options_state_changed)
        self.global_options_purge_docker_images_pushbutton.clicked.connect(self.on_purge_docker_images_options_clicked)
        self.global_options_purge_models_pushbutton.clicked.connect(self.on_purge_models_options_clicked)

    def on_test_docker_button_pressed(self):
        cmd = []
        cmd.append(self.dockerPath.currentPath)
        cmd.append('--version')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        message = p.stdout.readline().decode("utf-8")
        if message.startswith('Docker version'):
            qt.QMessageBox.information(None, 'Docker Status', 'Docker is configured correctly'
                                                              ' ({}).'.format(message))
        else:
            qt.QMessageBox.critical(None, 'Docker Status', 'Docker is not configured correctly. Check your docker '
                                                           'installation and make sure that it is configured to '
                                                           'be run by non-root user.')

    def on_task_tabwidget_tabchanged(self):
        # @TODO. Should a clean-up be performed when moving between segmentation and diagnostic tasks?
        # self.tasks_tabwidget.currentWidget().reload()
        pass

    def on_logic_event_start(self, task):
        if task == 'segmentation':
            self.base_segmentation_widget.on_logic_event_start()
        elif task == 'reporting':
            self.base_diagnosis_widget.on_logic_event_start()

    def on_logic_event_end(self, task):
        if task == 'segmentation':
            self.base_segmentation_widget.on_logic_event_end()
        elif task == 'reporting':
            self.base_diagnosis_widget.on_logic_event_end()

    def on_logic_event_abort(self, task):
        # @TODO: specific clean-up/reloading when the logic was aborted?
        pass

    def on_logic_log_event(self, log):
        self.logging_textedit.append(log)

    def on_logic_event_progress(self, task, progress, log):
        if task == 'segmentation':
            self.base_segmentation_widget.on_logic_event_progress(progress, log)
        elif task == 'reporting':
            self.base_diagnosis_widget.on_logic_event_progress(progress, log)

    def on_models_active_update_options_state_changed(self, state):
        SharedResources.getInstance().global_active_model_update = False if state == 0 else True

    def on_purge_docker_images_options_clicked(self):
        popup = WarningDialog()
        popup.setText("""Open the Docker Desktop Application and delete the following image: dbouget/raidionics-rads:v1.3\n
        Alternatively, write the following in a command line window: docker image rm dbouget/raidionics-rads:v1.3""")
        code = popup.exec()

    def on_purge_models_options_clicked(self):
        popup = WarningDialog()
        popup.setText("Are you sure you want to delete all local Raidionics models?")
        code = popup.exec()

        if code == 1:
            try:
                logging.info("Deleting all local json from {}.".format(SharedResources.getInstance().json_local_dir))
                if os.path.isdir(SharedResources.getInstance().json_local_dir):
                    shutil.rmtree(SharedResources.getInstance().json_local_dir)
                    os.makedirs(SharedResources.getInstance().json_local_dir)
                logging.info("Deleting all models from {}.".format(SharedResources.getInstance().model_path))
                if os.path.isdir(SharedResources.getInstance().model_path):
                    shutil.rmtree(SharedResources.getInstance().model_path)
                    os.makedirs(SharedResources.getInstance().model_path)
                logging.info("Deleting all pipelines from {}.".format(SharedResources.getInstance().diagnosis_path))
                if os.path.isdir(SharedResources.getInstance().diagnosis_path):
                    shutil.rmtree(SharedResources.getInstance().diagnosis_path)
                    os.makedirs(SharedResources.getInstance().diagnosis_path)
                if os.path.isdir(os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache')):
                    shutil.rmtree(os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache'))
                    os.makedirs(os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache'))
                # @TODO. Should send a signal to refresh both local models boxes in segmentation and RADS
            except Exception as e:
                logging.error("Purging local models failed.")
                logging.error(traceback.format_exc())
                logging.error("Please manually delete the following folders: {}, {}, {}.".format(SharedResources.getInstance().json_local_dir,
                              SharedResources.getInstance().model_path, SharedResources.getInstance().diagnosis_path))

    def set_default(self):
            self.base_segmentation_widget.set_default()
            self.base_diagnosis_widget.set_default()
