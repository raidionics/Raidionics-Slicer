import traceback

from slicer.ScriptedLoadableModule import *
import logging
import sys

if sys.version_info.major == 3:
    from queue import Queue
else:
    from Queue import Queue

import json
import platform
import os
import numpy
import re
import subprocess
import shutil
import threading
import csv
from collections import OrderedDict
from glob import glob
from time import sleep
from copy import deepcopy
from __main__ import qt, ctk, slicer, vtk

import SimpleITK as sitk
import sitkUtils
from src.utils.resources import SharedResources
from src.utils.backend_utilities import generate_backend_config


class RaidionicsLogic:
    """
    Singleton logic class, interfacing the backend where the processing happens.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if RaidionicsLogic.__instance == None:
            RaidionicsLogic()
        return RaidionicsLogic.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if RaidionicsLogic.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            RaidionicsLogic.__instance = self
            self.__init_base_variables()

    def __init_base_variables(self):
        self.abort = False
        self.dockerPath = SharedResources.getInstance().docker_path
        self.file_extension_docker = '.nii.gz'
        self.logic_task = 'segmentation'  # segmentation or diagnosis (RADS) for now
        self.logic_target_space = "neuro_diagnosis"

    def yieldPythonGIL(self, seconds=0):
        sleep(seconds)

    def start_logic(self):
        self.main_queue = Queue()
        self.main_queue_running = False
        self.thread = threading.Thread()
        self.cmdStartLogic()

    def stop_logic(self):
        if self.main_queue_running:
            self.main_queue_stop()
        if self.thread.is_alive():
            self.thread.join()
        self.cmdStopLogic()

    def main_queue_start(self):
        """
        Begins monitoring of main_queue for callables
        """
        self.main_queue_running = True
        # slicer.modules.RaidionicsWidget.onLogicRunStart()
        qt.QTimer.singleShot(0, self.main_queue_process)

    def main_queue_stop(self):
        """
        End monitoring of main_queue for callables
        """
        self.main_queue_running = False
        if self.thread.is_alive():
            self.thread.join()
        # slicer.modules.RaidionicsWidget.onLogicRunStop()

    def main_queue_process(self):
        """
        processes the main_queue of callables
        """
        try:
            while not self.main_queue.empty():
                f = self.main_queue.get_nowait()
                if callable(f):
                    f()

            if self.main_queue_running:
                # Yield the GIL to allow other thread to do some python work.
                # This is needed since pyQt doesn't yield the python GIL
                self.yieldPythonGIL(.01)
                qt.QTimer.singleShot(0, self.main_queue_process)

        except Exception as e:
            import sys
            sys.stderr.write("ModelLogic error in main_queue: \"{0}\"".format(e))

            # if there was an error try to resume
            if not self.main_queue.empty() or self.main_queue_running:
                qt.QTimer.singleShot(0, self.main_queue_process)

    def run(self, model_parameters):
        """
        Run the actual algorithm
        """
        self.cmdLogEvent('Starting the task.')
        self.start_logic()
        if self.thread.is_alive():
            import sys
            sys.stderr.write("ModelLogic is already executing!")
            return
        self.abort = False
        self.thread = threading.Thread(target=self.thread_doit(model_parameters=model_parameters))
        # self.stop_logic()  # stop_logic also performed in the thread_doit, which spot is the best to run it?

    def cancel_run(self):
        self.abort = True

    def thread_doit(self, model_parameters):
        iodict = model_parameters.iodict
        inputs = model_parameters.inputs
        params = model_parameters.params
        outputs = model_parameters.outputs
        dockerName = model_parameters.dockerImageName
        modelName = model_parameters.modelName
        modelTarget = model_parameters.modelTarget
        dataPath = model_parameters.dataPath
        widgets = model_parameters.widgets
        # The Docker image existence should have been checked when the model was selected.
        go_flag = self.check_docker_image_local_existence(docker_image_name=dockerName)
        if not go_flag:
            self.cmdLogEvent('The docker image does not exist, or could not be downloaded locally.\n'
                             'The selected model cannot be run.')
            return

        try:
            self.main_queue_start()
            self.logic_target_space = "neuro_diagnosis" if modelTarget == "Neuro" else "mediastinum_diagnosis"

            self.executeDocker(dockerName, modelName, dataPath, iodict, inputs, outputs, params, widgets)
            if not self.abort:
                self.updateOutput(iodict, outputs, widgets)
                # self.main_queue_stop()
                self.stop_logic()
                # self.cmdEndEvent()
            else:
                self.cmdAbortEvent()
        except Exception as e:
            self.cmdAbortEvent()
        '''
        except Exception as e:
            msg = e.message
            qt.QMessageBox.critical(slicer.util.mainWindow(), "Exception during execution of ", msg)
            slicer.modules.RaidionicsWidget.applyButton.enabled = True
            slicer.modules.RaidionicsWidget.progress.hide = True
            self.abort = True
            self.yieldPythonGIL()
        '''

    def cmdStartLogic(self):
        if hasattr(slicer.modules, 'RaidionicsWidget'):
            widget = slicer.modules.RaidionicsWidget
            widget.on_logic_event_start(self.logic_task)

    def cmdStopLogic(self):
        if hasattr(slicer.modules, 'RaidionicsWidget'):
            widget = slicer.modules.RaidionicsWidget
            widget.on_logic_event_end(self.logic_task)

    def cmdAbortEvent(self):
        """
        User chose to cancel the logic run, or something crashed along the way.
        In both cases, clean/reset methods should be called
        :return:
        """
        if hasattr(slicer.modules, 'RaidionicsWidget'):
            widget = slicer.modules.RaidionicsWidget
            widget.set_default()

    def cmdProgressEvent(self, progress, line):
        if hasattr(slicer.modules, 'RaidionicsWidget'):
            widget = slicer.modules.RaidionicsWidget
            widget.on_logic_event_progress(self.logic_task, progress, line)

    def cmdLogEvent(self, line):
        if hasattr(slicer.modules, 'RaidionicsWidget'):
            widget = slicer.modules.RaidionicsWidget
            widget.on_logic_log_event(line)

    def cmdCheckAbort(self, p):
        if self.abort:
            p.kill()
            # self.cmdAbortEvent()

    def checkDockerDaemon(self):
        cmd = list()
        cmd.append(self.dockerPath)
        cmd.append('ps')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        slicer.app.processEvents()
        line = p.stdout.readline().decode("utf-8")
        if line[:9] == 'CONTAINER':
            return True
        return False

    def check_docker_image_local_existence(self, docker_image_name):
        # Verify if the docker image exists on disk
        result = False
        cmd_docker = [self.dockerPath, 'image', 'inspect', docker_image_name]
        p = subprocess.Popen(cmd_docker, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        if 'Error: No such image' not in stderr.decode("utf-8"):
            result = True
        # res_lines = ""
        # while True:
        #     slicer.app.processEvents()
        #     line = p.stderr.readline().decode("utf-8")
        #     if not line:
        #         break
        #     res_lines = res_lines + '/n' + line
        #
        # # If the image has not been found, attempt to download it
        # if 'Error: No such image' not in res_lines:
        #     result = True

        return result

    # @TODO. Deprecated, to remove.
    def checkDockerImageLocalExistence(self, docker_image_name):
        # Verify if the docker image exists on disk, or ask to download it
        result = False
        cmd_docker = [self.dockerPath, 'image', 'inspect', docker_image_name]
        p = subprocess.Popen(cmd_docker, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # res_lines = ""
        # while True:
        #     slicer.app.processEvents()
        #     line = p.stderr.readline().decode("utf-8")
        #     if not line:
        #         break
        #     res_lines = res_lines + '/n' + line

        stdout, stderr = p.communicate()

        # If the image has not been found, attempt to download it
        if 'Error: No such image' in stderr.decode("utf-8"):
        # if 'Error: No such image' in res_lines:
            cmd_docker = [self.dockerPath, 'image', 'pull', docker_image_name]
            p2 = subprocess.Popen(cmd_docker, stdout=subprocess.PIPE)
            cmd_docker = [self.dockerPath, 'image', 'inspect', docker_image_name]
            p2 = subprocess.Popen(cmd_docker, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout2, stderr2 = p2.communicate()
            # If the image could not be downloaded -- abort
            if 'Error: No such image' in stderr2.decode("utf-8"):
                result = False
            else:
                result = True
            # res_lines = ""
            # while True:
            #     slicer.app.processEvents()
            #     line = p.stderr.readline().decode("utf-8")
            #     if not line:
            #         break
            #     res_lines = res_lines + '/n' + line
            #
            # # If the image could not be downloaded -- abort
            # if 'Error: No such image' in res_lines:
            #     result = False
            # else:
            #     result = True
        else:
            result = True

        return result

    def executeDocker(self, dockerName, modelName, dataPath, iodict, inputs, outputs, params, widgets):
        try:
            assert self.checkDockerDaemon(), "Docker Daemon is not running"
        except Exception as e:
            print(e.message)
            self.abort = True

        modules = slicer.modules
        if hasattr(modules, 'RaidionicsWidget'):
            widgetPresent = True
        else:
            widgetPresent = False

        dataPath = '/home/ubuntu/resources'
        if self.logic_task == 'diagnosis':
            dataPath = '/home/ubuntu/Raidionics-segmenter/resources'

        # if widgetPresent:
        #     self.cmdStartEvent()
        try:
            inputDict = dict()
            outputDict = dict()
            paramDict = dict()
            for item in iodict:
                if iodict[item]["iotype"] == "output":
                    if iodict[item]["type"] == "volume":
                        outputDict[item] = item
                        # curr_output = outputs[item]
                        nodes = slicer.util.getNodes(outputDict[item])
                        manual_node = widgets[[x.accessibleName == item + '_combobox' for x in widgets].index(True)].currentNode()
                        if len(nodes) == 0 and manual_node is None:
                            # If the output volume is not set, a new one is created
                            node = slicer.vtkMRMLLabelMapVolumeNode()
                            node.SetName(outputDict[item])
                            slicer.mrmlScene.AddNode(node)
                            node.CreateDefaultDisplayNodes()
                            if iodict[item]["voltype"] == "LabelMap":
                                imageData = vtk.vtkImageData()
                                imageData.SetDimensions((150, 150, 150))
                                imageData.AllocateScalars(vtk.VTK_SHORT, 1)
                                node.SetAndObserveImageData(imageData)
                            outputs[item] = node

                            # Select the correct item in the combobox upon creation
                            combobox_widget = widgets[[x.accessibleName == item + '_combobox' for x in widgets].index(True)]
                            combobox_widget.setCurrentNode(node)
                        elif not manual_node is None and not manual_node.GetImageData() is None:
                            # If the node links to a manually imported volume, used as input (e.g., for faster diagnosis)
                            # Working only if pointing to a file, not if a new empty LabelMapVolume was created.
                            outputs[item] = manual_node
                            output_node_name = outputs[item].GetName()
                            img = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(output_node_name))
                            fileName = item + self.file_extension_docker
                            # inputDict[item] = fileName
                            SharedResources.getInstance().user_diagnosis_configuration['Neuro'][item.lower() + '_segmentation_filename'] = os.path.join(dataPath, 'data', fileName)
                            sitk.WriteImage(img, str(os.path.join(SharedResources.getInstance().data_path, fileName)))
                        elif manual_node.GetImageData() is None:
                            # If the placeholder was manually created, but not linked to an image container
                            imageData = vtk.vtkImageData()
                            imageData.SetDimensions((150, 150, 150))
                            imageData.AllocateScalars(vtk.VTK_SHORT, 1)
                            manual_node.SetAndObserveImageData(imageData)

                    elif iodict[item]["type"] == "point_vec":
                        outputDict[item] = item + '.fcsv'
                    elif iodict[item]["type"] == "text":
                        outputDict[item] = item + '.txt'
                    else:
                        paramDict[item] = str(params[item])
            for item in iodict:
                if iodict[item]["iotype"] == "input":
                    if iodict[item]["type"] == "volume":
                        # print(inputs[item])
                        input_node_name = inputs[item].GetName()
                        try:
                            img = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(input_node_name))
                            input_sequence_type = iodict[item]["sequence_type"]
                            fileName = 'input_' + input_sequence_type + self.file_extension_docker
                            # @TODO. hard-coding to improve.
                            if input_sequence_type == "T1-CE":
                                fileName = 'input_t1gd' + self.file_extension_docker
                            inputDict[item] = fileName
                            input_timestamp_order = iodict[item]["timestamp_order"]
                            os.makedirs(str(os.path.join(SharedResources.getInstance().data_path, "T" + input_timestamp_order)))
                            sitk.WriteImage(img, str(os.path.join(SharedResources.getInstance().data_path,
                                                                  "T" + input_timestamp_order, fileName)))
                        except Exception as e:
                            print("Issue preparing input volume.")
                            print(traceback.format_exc())
                    elif iodict[item]["type"] == "configuration":
                        generate_backend_config(SharedResources.getInstance().data_path,
                                                iodict, self.logic_target_space, modelName)
                elif iodict[item]["iotype"] == "parameter":
                    paramDict[item] = str(params[item])
        except Exception:
            print("Error during inputs preparation before Docker call.")
            print(traceback.format_exc())

        self.cmdLogEvent('Docker run command:')

        cmd = list()
        cmd.append(self.dockerPath)
        cmd.extend(('run', '-t', '-v'))
        # if self.use_gpu:
        #     cmd.append(' --runtime=nvidia ')
        #cmd.append(TMP_PATH + ':' + dataPath)
        cmd.append(SharedResources.getInstance().resources_path + ':' + dataPath)
        cmd.append(dockerName)
        cmd.append('-c')
        cmd.append('/home/ubuntu/resources/data/rads_config.ini')
        cmd.append('-v')
        cmd.append('debug')

        self.cmdLogEvent(cmd)

        # try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        progress = 0
        # print('executing')
        while True:
            progress += 0.15
            slicer.app.processEvents()
            self.cmdCheckAbort(p)
            line = p.stdout.readline().decode("utf-8")
            if not line:
                break

            if widgetPresent:
                self.cmdLogEvent(line)
                self.cmdProgressEvent(progress, line)
            # print(line)

    def updateOutput(self, iodict, outputs, widgets):
        output_volume_files = dict()
        output_fiduciallist_files = dict()
        output_text_files = dict()
        self.output_raw_values = dict()
        created_files = []
        # @TODO. Have to fetch from the json files the correct timestamp for the task, to know in which folder to look.
        for _, _, files in os.walk(os.path.join(SharedResources.getInstance().output_path, 'T0')):
            for f, file in enumerate(files):
                created_files.append(file)
            break

        for item in iodict:
            if iodict[item]["iotype"] == "output":
                if iodict[item]["type"] == "volume":
                    # @TODO. Better way to disambiguate between output.nii.gz and output_description.csv for example?
                    fileName = str(os.path.join(SharedResources.getInstance().output_path, 'T0', created_files[[item+'.' in x for x in created_files].index(True)]))
                    output_volume_files[item] = fileName
                if iodict[item]["type"] == "point_vec":
                    fileName = str(os.path.join(SharedResources.getInstance().output_path, 'T0', item + '.fcsv'))
                    output_fiduciallist_files[item] = fileName
                if iodict[item]["type"] == "text":
                    fileName = str(os.path.join(SharedResources.getInstance().output_path, 'T0', item + '.txt'))
                    output_text_files[item] = fileName

        for output_volume in output_volume_files.keys():
            result = sitk.ReadImage(output_volume_files[output_volume])
            # print(result.GetPixelIDTypeAsString())
            self.output_raw_values[output_volume] = deepcopy(sitk.GetArrayFromImage(result))
            output_node = outputs[output_volume]
            output_node_name = output_node.GetName()
            # if iodict[output_volume]["voltype"] == 'LabelMap':
            nodeWriteAddress = sitkUtils.GetSlicerITKReadWriteAddress(output_node_name)
            self.display_port = nodeWriteAddress
            sitk.WriteImage(result, nodeWriteAddress)
            applicationLogic = slicer.app.applicationLogic()
            selectionNode = applicationLogic.GetSelectionNode()

            outputLabelMap = True
            if outputLabelMap:
                selectionNode.SetReferenceActiveLabelVolumeID(output_node.GetID())
            else:
                selectionNode.SetReferenceActiveVolumeID(output_node.GetID())

            applicationLogic.PropagateVolumeSelection(0)
            applicationLogic.FitSliceToAll()

        for fiduciallist in output_fiduciallist_files.keys():
            # information about loading markups: https://www.slicer.org/wiki/Documentation/Nightly/Modules/Markups
            output_node = outputs[fiduciallist]
            _, node = slicer.util.loadMarkupsFiducialList(output_fiduciallist_files[fiduciallist], True)
            output_node.Copy(node)
            scene = slicer.mrmlScene
            # todo: currently due to a bug in markups module removing the node will create some unexpected behaviors
            # reported bug reference: https://issues.slicer.org/view.php?id=4414
            # scene.RemoveNode(node)
        for text_key in output_text_files.keys():
            text_file = output_text_files[text_key]
            f = open(text_file, 'r')
            current_text = f.read()
            current_widget = widgets[[x.accessibleName == text_key for x in widgets].index(True)]
            current_widget.setPlainText(current_text)
            f.close()
