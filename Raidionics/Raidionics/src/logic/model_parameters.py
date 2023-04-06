from __main__ import qt, ctk, slicer, vtk
import SimpleITK as sitk
import sitkUtils
import re
from src.utils.resources import SharedResources


class ModelParameters(object):
    """
    Class for managing the widgets related to a model's parameters
    """

    # class-scope regular expression to help covert from CamelCase
    reCamelCase = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

    def __init__(self, parent=None):
        self.parent = parent
        self.widgets = []
        self.json = None
        # self.model = None
        self.inputs = []
        self.outputs = []
        self.segmentations = dict()
        self.segmentations_descriptions = dict()
        self.prerun_callbacks = []
        self.outputLabelMap = False
        self.iodict = dict()
        self.dockerImageName = ''
        self.modelName = None
        self.dataPath = None

        self.outputSelector = None
        self.outputLabelMapBox = None

    def __del__(self):
        self.widgets = []

    def BeautifyCamelCase(self, str):
        return self.reCamelCase.sub(r' \1', str)

    def create_iodict(self, json_dict):
        iodict = dict()
        for member in json_dict["members"]:
            if "type" in member:
                t = member["type"]
                if t in ["uint8_t", "int8_t",
                           "uint16_t", "int16_t",
                           "uint32_t", "int32_t",
                           "uint64_t", "int64_t",
                           "unsigned int", "int",
                           "double", "float"]:
                    iodict[member["name"]] = {"type": member["type"], "iotype": member["iotype"],
                                                            "value": member["default"]}
                elif t in ["volume"]:
                    iodict[member["name"]] = {"type": member["type"], "iotype": member["iotype"],
                                              "voltype": member["voltype"]}
                    if 'importance' in member:
                        iodict[member["name"]]['importance'] = member['importance']
                    if 'sequence_type' in member:
                        iodict[member["name"]]['sequence_type'] = member['sequence_type']
                    if 'timestamp_order' in member:
                        iodict[member["name"]]['timestamp_order'] = member['timestamp_order']
                    if 'description' in member:
                        iodict[member["name"]]['description'] = member['description']
                    if 'threshold' in member:
                        iodict[member["name"]]['threshold'] = member['threshold']
                    if 'color' in member:
                        iodict[member["name"]]['color'] = member['color']
                    if 'atlas_category' in member:
                        iodict[member["name"]]['atlas_category'] = member['atlas_category']
                elif t in ["configuration"]:
                    iodict[member["name"]] = {"type": member["type"], "iotype": member["iotype"]}
                    if 'default' in member:
                        iodict[member["name"]]['default'] = member['default']
                elif t in ["text"]:
                    iodict[member["name"]] = {"type": member["type"], "iotype": member["iotype"]}
                    if 'default' in member:
                        iodict[member["name"]]['default'] = member['default']
                else:
                    iodict[member["name"]] = {"type": member["type"], "iotype": member["iotype"]}
        return iodict

    def create_model_info(self, json_dict):
        dockerImageName = json_dict['docker']['dockerhub_repository']
        modelName = json_dict.get('model_name')
        modelTarget = json_dict.get('target')
        dataPath = json_dict.get('data_path')
        return dockerImageName, modelName, modelTarget, dataPath

    def create(self, json_dict):
        if not self.parent:
            raise "no parent"
            # parametersFormLayout = self.parent.layout()

        # You can't use exec in a function that has a subfunction, unless you specify a context.
        # exec ('self.model = sitk.{0}()'.format(json["name"])) in globals(), locals()

        self.json_dict = json_dict
        self.iodict = self.create_iodict(json_dict)
        self.dockerImageName, self.modelName, self.modelTarget, self.dataPath = self.create_model_info(json_dict)

        self.prerun_callbacks = []
        self.inputs = dict()
        self.outputs = dict()
        self.params = dict()
        self.outputLabelMap = False
        #
        # Iterate over the members in the JSON to generate a GUI
        #
        for member in json_dict["members"]:
            w = None
            if "type" in member:
                t = member["type"]

            if "dim_vec" in member and int(member["dim_vec"]):
                if member["itk_type"].endswith("IndexType") or member["itk_type"].endswith("PointType"):
                    isPoint = member["itk_type"].endswith("PointType")

                    fiducialSelector = slicer.qMRMLNodeComboBox()
                    self.widgets.append(fiducialSelector)
                    fiducialSelector.nodeTypes = ("vtkMRMLMarkupsFiducialNode", "vtkMRMLAnnotationFiducialNode")
                    fiducialSelector.selectNodeUponCreation = True
                    fiducialSelector.addEnabled = False
                    fiducialSelector.removeEnabled = False
                    fiducialSelector.renameEnabled = True
                    fiducialSelector.noneEnabled = False
                    fiducialSelector.showHidden = False
                    fiducialSelector.showChildNodeTypes = True
                    fiducialSelector.setMRMLScene(slicer.mrmlScene)
                    fiducialSelector.setToolTip("Pick the Fiducial for the Point or Index")

                    fiducialSelector.connect("nodeActivated(vtkMRMLNode*)",
                                             lambda node, w=fiducialSelector, name=member["name"],
                                                    isPt=isPoint: self.onFiducialNode(name, w, isPt))
                    self.prerun_callbacks.append(
                        lambda w=fiducialSelector, name=member["name"], isPt=isPoint: self.onFiducialNode(name, w,
                                                                                                          isPt))

                    w1 = fiducialSelector

                    fiducialSelectorLabel = qt.QLabel("{0}: ".format(member["name"]))
                    self.widgets.append(fiducialSelectorLabel)

                    icon = qt.QIcon(SharedResources.getInstance().icon_dir + "Fiducials.png")

                    toggle = qt.QPushButton(icon, "")
                    toggle.setCheckable(True)
                    toggle.toolTip = "Toggle Fiducial Selection"
                    self.widgets.append(toggle)

                    w2 = self.createVectorWidget(member["name"], t)

                    hlayout = qt.QHBoxLayout()
                    hlayout.addWidget(fiducialSelector)
                    hlayout.setStretchFactor(fiducialSelector, 1)
                    hlayout.addWidget(w2)
                    hlayout.setStretchFactor(w2, 1)
                    hlayout.addWidget(toggle)
                    hlayout.setStretchFactor(toggle, 0)
                    w1.hide()

                    self.widgets.append(hlayout)

                    toggle.connect("clicked(bool)",
                                   lambda checked, ptW=w2, fidW=w1: self.onToggledPointSelector(checked, ptW, fidW))

                    # parametersFormLayout.addRow(fiducialSelectorLabel, hlayout)

                else:
                    w = self.createVectorWidget(member["name"], t)

            elif t == "point_vec":

                fiducialSelector = slicer.qMRMLNodeComboBox()
                self.widgets.append(fiducialSelector)
                fiducialSelector.nodeTypes = ("vtkMRMLMarkupsFiducialNode", "vtkMRMLAnnotationHierarchyNode")
                fiducialSelector.addAttribute("vtkMRMLAnnotationHierarchyNode", "MainChildType",
                                              "vtkMRMLAnnotationFiducialNode")
                fiducialSelector.selectNodeUponCreation = True
                fiducialSelector.addEnabled = True
                fiducialSelector.removeEnabled = False
                fiducialSelector.renameEnabled = True
                fiducialSelector.noneEnabled = False
                fiducialSelector.showHidden = False
                fiducialSelector.showChildNodeTypes = True
                fiducialSelector.setMRMLScene(slicer.mrmlScene)
                fiducialSelector.setToolTip("Pick the Markups node for the point list.")


                fiducialSelector.connect("nodeActivated(vtkMRMLNode*)",
                                         lambda node, name=member["name"]: self.onFiducialListNode(name, node, member["iotype"]))
                self.prerun_callbacks.append(
                    lambda w=fiducialSelector, name=member["name"], : self.onFiducialListNode(name, w.currentNode(), member["iotype"]))

                w = fiducialSelector

            elif "enum" in member:
                w = self.createEnumWidget(member["name"], member["enum"])

            elif member["name"].endswith("Direction") and "std::vector" in t:
                # This member name is use for direction cosine matrix for image sources.
                # We are going to ignore it
                pass
            elif t == "volume":
                cname = member["name"]
                w = self.createVolumeWidget(cname, member["iotype"], member["voltype"], False)

            elif t == "InterpolatorEnum":
                labels = ["Nearest Neighbor",
                          "Linear",
                          "BSpline",
                          "Gaussian",
                          "Label Gaussian",
                          "Hamming Windowed Sinc",
                          "Cosine Windowed Sinc",
                          "Welch Windowed Sinc",
                          "Lanczos Windowed Sinc",
                          "Blackman Windowed Sinc"]
                values = ["sitk.sitkNearestNeighbor",
                          "sitk.sitkLinear",
                          "sitk.sitkBSpline",
                          "sitk.sitkGaussian",
                          "sitk.sitkLabelGaussian",
                          "sitk.sitkHammingWindowedSinc",
                          "sitk.sitkCosineWindowedSinc",
                          "sitk.sitkWelchWindowedSinc",
                          "sitk.sitkLanczosWindowedSinc",
                          "sitk.sitkBlackmanWindowedSinc"]

                w = self.createEnumWidget(member["name"], labels, values)
                pass
            elif t == "PixelIDValueEnum":
                labels = ["int8_t",
                          "uint8_t",
                          "int16_t",
                          "uint16_t",
                          "uint32_t",
                          "int32_t",
                          "float",
                          "double"]
                values = ["sitk.sitkInt8",
                          "sitk.sitkUInt8",
                          "sitk.sitkInt16",
                          "sitk.sitkUInt16",
                          "sitk.sitkInt32",
                          "sitk.sitkUInt32",
                          "sitk.sitkFloat32",
                          "sitk.sitkFloat64"]
                w = self.createEnumWidget(member["name"], labels, values)
            elif t in ["double", "float"]:
                w = self.createDoubleWidget(member["name"], default=member["default"])
            elif t == "bool":
                w = self.createBoolWidget(member["name"], default=member["default"])
            elif t == "str":
                w = self.createStringWidget(member["name"], default=member["default"])
            elif t == "configuration":
                pass
            elif t == "text":
                # w = self.createTextWidget(member["name"], default=member["default"])
                pass
            elif t in ["uint8_t", "int8_t",
                       "uint16_t", "int16_t",
                       "uint32_t", "int32_t",
                       "uint64_t", "int64_t",
                       "unsigned int", "int"]:
                w = self.createIntWidget(member["name"], t, default=member["default"])
            else:
                import sys
                sys.stderr.write("Unknown member \"{0}\" of type \"{1}\"\n".format(member["name"], member["type"]))

            if w:
                self.addWidgetWithToolTipAndLabel(w, member)

    def createVolumeWidget(self, name, iotype, voltype, noneEnabled=False):
        # print("create volume widget : {0}".format(name))
        volumeSelector = slicer.qMRMLNodeComboBox()
        self.widgets.append(volumeSelector)
        if voltype == 'ScalarVolume':
            volumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode", ]
        elif voltype == 'LabelMap':
            volumeSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode", ]
        # elif voltype == 'Segmentation':
        #     volumeSelector.nodeTypes = ["vtkMRMLSegmentationNode", ]
        else:
            print('Voltype must be either ScalarVolume or LabelMap!')
        volumeSelector.selectNodeUponCreation = True
        if iotype == "input":
            volumeSelector.addEnabled = False
        elif iotype == "output":
            volumeSelector.addEnabled = True
            volumeSelector.accessibleName = name + '_combobox'
        volumeSelector.renameEnabled = True
        volumeSelector.removeEnabled = True
        volumeSelector.noneEnabled = noneEnabled
        volumeSelector.showHidden = False
        volumeSelector.showChildNodeTypes = False
        volumeSelector.setMRMLScene(slicer.mrmlScene)
        volumeSelector.setToolTip("Pick the volume.")

        # connect and verify parameters
        volumeSelector.connect("currentNodeChanged(vtkMRMLNode*)",
                               lambda node, n=name, io=iotype: self.onVolumeSelect(node, n, io))
        if iotype == "input":
            self.inputs[name] = volumeSelector.currentNode()
        elif iotype == "output":
            self.outputs[name] = volumeSelector.currentNode()

        return volumeSelector

    def createEnumWidget(self, name, enumList, valueList=None):

        w = qt.QComboBox()
        self.widgets.append(w)

        # exec 'default=self.model.Get{0}()'.format(name) in globals(), locals()

        if valueList is None:
            valueList = ["self.model." + e for e in enumList]

        for e, v in zip(enumList, valueList):
            w.addItem(e, v)

        self.params[name] = w.currentText
        w.connect("currentIndexChanged(int)",
                  lambda selectorIndex, n=name, selector=w: self.onEnumChanged(n, selectorIndex, selector))
        return w

    def createVectorWidget(self, name, type):
        m = re.search(r"<([a-zA-Z ]+)>", type)
        if m:
            type = m.group(1)

        w = ctk.ctkCoordinatesWidget()
        self.widgets.append(w)

        if type in ["double", "float"]:
            w.setDecimals(5)
            w.minimum = -3.40282e+038
            w.maximum = 3.40282e+038
            w.connect("coordinatesChanged(double*)",
                      lambda val, widget=w, name=name: self.onFloatVectorChanged(name, widget, val))
        elif type == "bool":
            w.setDecimals(0)
            w.minimum = 0
            w.maximum = 1
            w.connect("coordinatesChanged(double*)",
                      lambda val, widget=w, name=name: self.onBoolVectorChanged(name, widget, val))
        else:
            w.setDecimals(0)
            w.connect("coordinatesChanged(double*)",
                      lambda val, widget=w, name=name: self.onIntVectorChanged(name, widget, val))

        # exec ('default = self.model.Get{0}()'.format(name)) in globals(), locals()
        # w.coordinates = ",".join(str(x) for x in default)
        return w

    def createIntWidget(self, name, type="int", default=None):

        w = qt.QSpinBox()
        self.widgets.append(w)

        if type == "uint8_t":
            w.setRange(0, 255)
        elif type == "int8_t":
            w.setRange(-128, 127)
        elif type == "uint16_t":
            w.setRange(0, 65535)
        elif type == "int16_t":
            w.setRange(-32678, 32767)
        elif type == "uint32_t" or type == "uint64_t" or type == "unsigned int":
            w.setRange(0, 2147483647)
        elif type == "int32_t" or type == "uint64_t" or type == "int":
            w.setRange(-2147483648, 2147483647)

        # exec ('default = self.model.Get{0}()'.format(name)) in globals(), locals()
        if default is not None:
            w.setValue(int(default))
        w.connect("valueChanged(int)", lambda val, name=name: self.onScalarChanged(name, val))
        return w

    def createBoolWidget(self, name, default):
        # print('create bool widget')
        w = qt.QCheckBox()
        self.widgets.append(w)
        if default == 'false':
            checked = False
        else:
            checked = True
        w.setChecked(checked)
        self.params[name] = int(w.checked)
        w.connect("stateChanged(int)", lambda val, name=name: self.onScalarChanged(name, int(val)))

        return w

    def createStringWidget(self, name, default):
        # print('create String widget')
        w = qt.QComboBox()
        self.widgets.append(w)
        w.addItem(default)
        w.setAccessibleName(name)
        self.params[name] = w.currentText
        w.connect("currentTextChanged(const QString &)", lambda val, name=name: self.onStringChanged(name, val))

        return w

    def createDoubleWidget(self, name, default=None):
        # exec ('default = self.model.Get{0}()'.format(name)) in globals(), locals()
        w = qt.QDoubleSpinBox()
        self.widgets.append(w)

        w.setRange(-3.40282e+038, 3.40282e+038)
        w.decimals = 5

        if default is not None:
            w.setValue(default)
        w.connect("valueChanged(double)", lambda val, name=name: self.onScalarChanged(name, val))

        return w

    def createTextWidget(self, name, default=None):
        # print('create String widget')
        w = qt.QTextEdit()
        self.widgets.append(w)
        w.setAccessibleName(name)
        self.params[name] = w.plainText
        # w.connect("currentTextChanged(const QString &)", lambda val, name=name: self.onStringChanged(name, val))
        w.setReadOnly(True)
        if default is not None:
            w.setPlainText(default)
        #
        # elif iotype == "output":
        #     self.outputs[name] = volumeSelector.currentNode()

        return w

    def addWidgetWithToolTipAndLabel(self, widget, memberJSON):
        tip = ""
        if "briefdescriptionSet" in memberJSON and len(memberJSON["briefdescriptionSet"]):
            tip = memberJSON["briefdescriptionSet"]
        elif "detaileddescriptionSet" in memberJSON:
            tip = memberJSON["detaileddescriptionSet"]
        elif "importance" in memberJSON and len(memberJSON["importance"]):
            tip = memberJSON["importance"]

        # remove trailing white space
        tip = tip.rstrip()

        l = qt.QLabel(self.BeautifyCamelCase(memberJSON["name"]) + ": ")
        if memberJSON["type"] == "volume":
            l.setText(self.BeautifyCamelCase("(" + memberJSON["iotype"] + ") " + memberJSON["name"]) + ": ")
        self.widgets.append(l)

        widget.setToolTip(tip)
        l.setToolTip(tip)

        parametersFormLayout = self.parent.layout()
        parametersFormLayout.addRow(l, widget)

    def onToggledPointSelector(self, fidVisible, ptWidget, fiducialWidget):
        ptWidget.setVisible(False)
        fiducialWidget.setVisible(False)

        ptWidget.setVisible(not fidVisible)
        fiducialWidget.setVisible(fidVisible)

        if ptWidget.visible:
            # Update the coordinate values to envoke the changed signal.
            # This will update the model from the widget
            ptWidget.coordinates = ",".join(str(x) for x in ptWidget.coordinates.split(','))

    def onVolumeSelect(self, mrmlNode, n, io):
        # print("on volume select:{}".format(n))
        if io == "input":
            self.inputs[n] = mrmlNode
        elif io == "output":
            self.outputs[n] = mrmlNode

    '''
    def onOutputSelect(self, mrmlNode):
        self.output = mrmlNode
        self.onOutputLabelMapChanged(mrmlNode.IsA("vtkMRMLLabelMapVolumeNode"))
    def onOutputLabelMapChanged(self, v):
        self.outputLabelMap = v
        self.outputLabelMapBox.setChecked(v)
    '''

    def onFiducialNode(self, name, mrmlWidget, isPoint):
        if not mrmlWidget.visible:
            return
        annotationFiducialNode = mrmlWidget.currentNode()

        # point in physical space
        coord = [0, 0, 0]

        if annotationFiducialNode.GetClassName() == "vtkMRMLMarkupsFiducialNode":
            # slicer4 Markups node
            if annotationFiducialNode.GetNumberOfFiducials() < 1:
                return
            annotationFiducialNode.GetNthFiducialPosition(0, coord)
        else:
            annotationFiducialNode.GetFiducialCoordinates(coord)

        # HACK transform from RAS to LPS
        coord = [-coord[0], -coord[1], coord[2]]

        # FIXME: we should not need to copy the image
        if not isPoint and len(self.inputs) and self.inputs[0]:
            imgNodeName = self.inputs[0].GetName()
            img = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(imgNodeName))
            coord = img.TransformPhysicalPointToIndex(coord)
            # exec ('self.model.Set{0}(coord)'.format(name))

    def onFiducialListNode(self, name, mrmlNode, io):
        self.params[name] = mrmlNode
        if io == "input":
            self.inputs[name] = mrmlNode
        elif io == "output":
            self.outputs[name] = mrmlNode

        '''
        annotationHierarchyNode = mrmlNode
        # list of points in physical space
        coords = []
        if annotationHierarchyNode.GetClassName() == "vtkMRMLMarkupsFiducialNode":
            # slicer4 Markups node
            for i in range(annotationHierarchyNode.GetNumberOfFiducials()):
                coord = [0, 0, 0]
                annotationHierarchyNode.GetNthFiducialPosition(i, coord)
                coords.append(coord)
        else:
            # slicer4 style hierarchy nodes
            # get the first in the list
            for listIndex in range(annotationHierarchyNode.GetNumberOfChildrenNodes()):
                if annotationHierarchyNode.GetNthChildNode(listIndex) is None:
                    continue
                annotation = annotationHierarchyNode.GetNthChildNode(listIndex).GetAssociatedNode()
                if annotation is None:
                    continue
                coord = [0, 0, 0]
                annotation.GetFiducialCoordinates(coord)
                coords.append(coord)
        if self.inputs[0]:
            imgNodeName = self.inputs[0].GetName()
            img = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(imgNodeName))
            # HACK transform from RAS to LPS
            coords = [[-pt[0], -pt[1], pt[2]] for pt in coords]
            idx_coords = [img.TransformPhysicalPointToIndex(pt) for pt in coords]
            # exec ('self.model.Set{0}(idx_coords)'.format(name))
        '''

    def onScalarChanged(self, name, val):
        # exec ('self.model.Set{0}(val)'.format(name))
        # print("onScalarChanged")
        self.params[name] = val

    def onStringChanged(self, name, val):
        # exec ('self.model.Set{0}(val)'.format(name))
        # print("onStringChanged")
        self.params[name] = val

    def onEnumChanged(self, name, selectorIndex, selector):
        # data = selector.itemData(selectorIndex)
        self.params[name] = selector.currentText

    def onBoolVectorChanged(self, name, widget, val):
        coords = [bool(float(x)) for x in widget.coordinates.split(',')]
        # exec ('self.model.Set{0}(coords)'.format(name))

    def onIntVectorChanged(self, name, widget, val):
        coords = [int(float(x)) for x in widget.coordinates.split(',')]
        # exec ('self.model.Set{0}(coords)'.format(name))

    def onFloatVectorChanged(self, name, widget, val):
        coords = [float(x) for x in widget.coordinates.split(',')]
        # exec ('self.model.Set{0}(coords)'.format(name))

    def prerun(self):
        print('prerun...')
        for f in self.prerun_callbacks:
            f()

    def destroy(self):
        self.iodict = dict()
        self.inputs = dict()
        self.outputs = dict()
        for w in self.widgets:
            # self.parent.layout().removeWidget(w)
            w.deleteLater()
            w.setParent(None)
        self.widgets = []