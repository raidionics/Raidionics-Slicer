from slicer.ScriptedLoadableModule import *

import os
import csv
from random import randint
from __main__ import qt, ctk, slicer, vtk

import SimpleITK as sitk
import sitkUtils
from src.utils.resources import SharedResources
from src.logic.mediastinum_diagnosis_result_parameters import *


class MediastinumDiagnosisSlicerInterface:
    """
    Singleton class...
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if MediastinumDiagnosisSlicerInterface.__instance == None:
            MediastinumDiagnosisSlicerInterface()
        return MediastinumDiagnosisSlicerInterface.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if MediastinumDiagnosisSlicerInterface.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MediastinumDiagnosisSlicerInterface.__instance = self
            self.__init_base_variables()

    def __init_base_variables(self):
        self.labelmap_nodes = dict()
        self.segmentation_nodes = dict()
        self.segmentation_nodes_descriptions = dict()

    def set_default(self):
        self.clear_view()

    def clear_view(self):
        if len(self.labelmap_nodes.keys()) != 0:
            for n in self.labelmap_nodes.keys():
                node = self.labelmap_nodes[n]
                slicer.mrmlScene.RemoveNode(node)
            self.labelmap_nodes = dict()

        if len(self.segmentation_nodes.keys()) != 0:
            for n in self.segmentation_nodes.keys():
                node = self.segmentation_nodes[n]
                slicer.mrmlScene.RemoveNode(node)
            self.segmentation_nodes = dict()
            self.segmentation_nodes_descriptions = dict()

    def generate_segmentations_from_labelmaps(self, model_parameters):
        """
        Create vtkMRMLSegmentationNode instances for each vtkMRMLLabelMap existing
        :param model_parameters:
        :return:
        """
        iodict = model_parameters.iodict
        outputs = model_parameters.outputs

        # If segments were created before, erase them and recompute?
        self.clear_view()

        for output in outputs.keys():
            try:
                if output != 'Tracts':
                    output_node = outputs[output]
                    seg_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
                    slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(output_node, seg_node)
                    seg_node.CreateClosedSurfaceRepresentation()
                    seg_node.SetName(output)
                    self.segmentation_nodes[output] = seg_node

                    if 'color' in iodict[output]:
                        detailed_color = [int(x) for x in iodict[output]['color'].split(',')]
                        detailed_color = [x / 255. for x in detailed_color]
                        #seg_node.SetColor(detailed_color[0], detailed_color[1], detailed_color[2])
                        seg_node.GetSegmentation().GetNthSegment(0).SetColor(detailed_color[0], detailed_color[1], detailed_color[2])

                    if 'description' in iodict[output] and iodict[output]['description'] == 'True':
                        desc_info = []
                        csv_filename = str(os.path.join(SharedResources.getInstance().output_path, output + '_description.csv'))
                        file = open(csv_filename, 'r')
                        csvfile = csv.DictReader(file)
                        for row in csvfile:
                            desc_info.append(dict(row))
                        file.close()

                        self.segmentation_nodes_descriptions[output] = desc_info

                        for l in desc_info:
                            segm = seg_node.GetSegmentation().GetNthSegment(int(l['label']))
                            if segm is not None:
                                segm.SetName(l['text'])
                else:
                    desc_info = []
                    csv_filename = str(
                        os.path.join(SharedResources.getInstance().output_path, output + '_description.csv'))
                    file = open(csv_filename, 'r')
                    csvfile = csv.DictReader(file)
                    for row in csvfile:
                        desc_info.append(dict(row))
                    file.close()

                    self.segmentation_nodes_descriptions[output] = desc_info
                    for l in desc_info:
                        item_name = l['text']
                        item_label_filename = os.path.join(SharedResources.getInstance().output_path,
                                                           '_'.join(item_name.split(' ')) + '_mni_tract_to_input.nii.gz')
                        if os.path.exists(item_label_filename):
                            node = slicer.vtkMRMLLabelMapVolumeNode()
                            node.SetName(item_name)
                            slicer.mrmlScene.AddNode(node)
                            node.CreateDefaultDisplayNodes()
                            imageData = vtk.vtkImageData()
                            imageData.SetDimensions((150, 150, 150))
                            imageData.AllocateScalars(vtk.VTK_SHORT, 1)
                            node.SetAndObserveImageData(imageData)
                            label_map = sitk.ReadImage(item_label_filename)
                            nodeWriteAddress = sitkUtils.GetSlicerITKReadWriteAddress(node)
                            sitk.WriteImage(label_map, nodeWriteAddress)
                            applicationLogic = slicer.app.applicationLogic()
                            selectionNode = applicationLogic.GetSelectionNode()
                            selectionNode.SetReferenceActiveLabelVolumeID(node.GetID())
                            applicationLogic.PropagateVolumeSelection(0)
                            applicationLogic.FitSliceToAll()
                            self.labelmap_nodes[item_name] = node

                            seg_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
                            slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(node, seg_node)
                            seg_node.CreateClosedSurfaceRepresentation()
                            seg_node.SetName(item_name)
                            detailed_color = [randint(0, 255), randint(0, 255), randint(0, 255)]
                            detailed_color = [x / 255. for x in detailed_color]
                            seg_node.GetSegmentation().GetNthSegment(0).SetColor(detailed_color[0], detailed_color[1],
                                                                                 detailed_color[2])
                            self.segmentation_nodes[item_name] = seg_node
                            # model_parameters.segmentations[output] = seg_node
                            # result = sitk.ReadImage(item_label_filename)
                            # output_node = outputs[output_volume]
                            # output_node_name = output_node.GetName()
                            # # if iodict[output_volume]["voltype"] == 'LabelMap':
                            # nodeWriteAddress = sitkUtils.GetSlicerITKReadWriteAddress(output_node_name)
                            # self.display_port = nodeWriteAddress
                            # sitk.WriteImage(result, nodeWriteAddress)
                            # applicationLogic = slicer.app.applicationLogic()
                            # selectionNode = applicationLogic.GetSelectionNode()
                            #
                            # outputLabelMap = True
                            # if outputLabelMap:
                            #     selectionNode.SetReferenceActiveLabelVolumeID(output_node.GetID())
                            # else:
                            #     selectionNode.SetReferenceActiveVolumeID(output_node.GetID())
                            #
                            # applicationLogic.PropagateVolumeSelection(0)
                            # applicationLogic.FitSliceToAll()

            except Exception as e:
                pass

    def on_optimal_display(self, model_parameters):
        """

        """
        pass
