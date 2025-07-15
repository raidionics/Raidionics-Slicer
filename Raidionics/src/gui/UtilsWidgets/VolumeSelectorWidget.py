import os
import slicer
from qt import QWidget, QHBoxLayout, QPushButton
from src.utils.resources import SharedResources


class VolumeSelectorWidget(QWidget):
    def __init__(self, params, noneEnabled=False, parent=None):
        super(VolumeSelectorWidget, self).__init__(parent)
        self.name = params["name"]
        self.iotype = params["iotype"]
        self.voltype = params["voltype"]
        self.mandatory = params["importance"] == "Mandatory" if "importance" in params.keys() else False
        self.noneEnabled = noneEnabled
        self.accessibleName = self.name + '_combobox'
        self.volume_layout = QHBoxLayout()
        self.setLayout(self.volume_layout)

        self.__set_interface()
        self.__set_dimensions()
        self.__set_stylesheet()
        self.__set_connections()

        if self.iotype == "output" or self.mandatory:
            self.activation_button.setEnabled(False)

    def __set_interface(self):
        self.volume_selector = slicer.qMRMLNodeComboBox()
        if self.voltype == 'ScalarVolume':
            self.volume_selector.nodeTypes = ["vtkMRMLScalarVolumeNode", ]
        elif self.voltype == 'LabelMap':
            self.volume_selector.nodeTypes = ["vtkMRMLLabelMapVolumeNode", ]
        # elif voltype == 'Segmentation':
        #     volumeSelector.nodeTypes = ["vtkMRMLSegmentationNode", ]
        else:
            print('Voltype must be either ScalarVolume or LabelMap!')
        self.volume_selector.selectNodeUponCreation = True
        if self.iotype == "input":
            self.volume_selector.addEnabled = False
        elif self.iotype == "output":
            self.volume_selector.addEnabled = True
            self.volume_selector.accessibleName = self.name + '_combobox'
        self.volume_selector.renameEnabled = True
        self.volume_selector.removeEnabled = True
        self.volume_selector.noneEnabled = self.noneEnabled
        self.volume_selector.showHidden = False
        self.volume_selector.showChildNodeTypes = False
        self.volume_selector.setMRMLScene(slicer.mrmlScene)
        self.volume_selector.setToolTip("Pick the volume.")
        self.activation_button = QPushButton()
        self.activation_button.setText("v")
        self.activation_button.setCheckable(True)
        self.activation_button.setToolTip("Press to enable (v) or disable (x)")

        self.volume_layout.addWidget(self.volume_selector)
        self.volume_layout.addWidget(self.activation_button)

    def __set_dimensions(self):
        # self.volume_selector.setMinimumSize(100, 50)
        self.setMinimumHeight(30)
        self.activation_button.setMaximumWidth(40)

    def __set_stylesheet(self):
        software_ss = SharedResources.getInstance().stylesheet_components
        font_size = software_ss["Font-size"]
        font_color = software_ss["Color7"]
        background_color = software_ss["White"]
        pressed_background_color = software_ss["Color6"]

    def __set_connections(self):
        self.activation_button.clicked.connect(self.onActivationPressed)

    def __reset_node(self):
        self.volume_selector.setCurrentNode(None)
        self.update()

    def onActivationPressed(self, state):
        self.__reset_node()
        if state:
            self.activation_button.setText("x")
            self.volume_selector.setDisabled(True)
        else:
            self.activation_button.setText("v")
            self.volume_selector.setDisabled(False)