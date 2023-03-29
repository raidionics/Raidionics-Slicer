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

        # Setting the Docker widget, necessary to run either a segmentation or diagnosis task
        self.setup_docker_widget()

        # # Reload and Test area
        # reloadCollapsibleButton = ctk.ctkCollapsibleButton()
        # reloadCollapsibleButton.collapsed = True
        # reloadCollapsibleButton.text = "Reload && Test"
        # reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)
        # # reload button
        # # (use this during development, but remove it when delivering
        # #  your module to users)
        # self.reloadButton = qt.QPushButton("Reload")
        # self.reloadButton.toolTip = "Reload this module."
        # self.reloadButton.name = "Freehand3DUltrasound Reload"
        # reloadFormLayout.addWidget(self.reloadButton)
        # self.reloadButton.connect('clicked()', self.onReload)
        # # uncomment the following line for debug/development.
        # self.layout.addWidget(reloadCollapsibleButton)
        # self.layout.addWidget(self.base_segmentation_widget)

        self.setup_global_options_widget()
        self.setup_user_interactions_widget()
        self.layout.addStretch(1)
        self.setup_connections()

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
        self.global_options_purge_docker_images_pushbutton.setToolTip("Click to purge the computer from old/unused Docker images (Not Implemented Yet).")
        self.global_options_groupbox_layout.addRow("Purge old Docker images:", self.global_options_purge_docker_images_pushbutton)
        # option 3: way to clean old models

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

    def setup_connections(self):
        self.docker_test_pushbutton.connect('clicked(bool)', self.on_test_docker_button_pressed)
        self.tasks_tabwidget.connect('currentChanged(int)', self.on_task_tabwidget_tabchanged)
        self.global_options_active_models_update_checkbox.stateChanged.connect(self.on_models_active_update_options_state_changed)
        self.global_options_purge_docker_images_pushbutton.clicked.connect(self.on_purge_docker_images_options_clicked)

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
        elif task == 'diagnosis':
            self.base_diagnosis_widget.on_logic_event_start()

    def on_logic_event_end(self, task):
        if task == 'segmentation':
            self.base_segmentation_widget.on_logic_event_end()
        elif task == 'diagnosis':
            self.base_diagnosis_widget.on_logic_event_end()

    def on_logic_event_abort(self, task):
        # @TODO: specific clean-up/reloading when the logic was aborted?
        pass

    def on_logic_log_event(self, log):
        self.logging_textedit.append(log)

    def on_logic_event_progress(self, task, progress, log):
        if task == 'segmentation':
            self.base_segmentation_widget.on_logic_event_progress(progress, log)
        elif task == 'diagnosis':
            self.base_diagnosis_widget.on_logic_event_progress(progress, log)

    def on_models_active_update_options_state_changed(self, state):
        SharedResources.getInstance().global_active_model_update = False if state == 0 else True

    def on_purge_docker_images_options_clicked(self):
        pass

    def set_default(self):
        self.base_segmentation_widget.set_default()
        self.base_diagnosis_widget.set_default()
