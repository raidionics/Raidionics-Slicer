from __main__ import qt, ctk, slicer, vtk
from glob import glob
import os
import json
from collections import OrderedDict
import subprocess

from src.utils.resources import SharedResources
from src.logic.model_parameters import *
from src.DeepSintefLogic import DeepSintefLogic


class DiagnosisInterfaceWidget(qt.QWidget):
    """
    GUI component displaying the selection of possible diagnosis available, very similar to the segmentation counter-part.
    """
    def __init__(self, parent=None):
        super(DiagnosisInterfaceWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.setup_local_diagnosis_area()
        self.setup_diagnosis_parameters_area()
        self.setLayout(self.base_layout)
        self.setup_connections()
        self.on_diagnosis_selection(0)

    def setup_local_diagnosis_area(self):
        self.local_diagnosis_area_groupbox = ctk.ctkCollapsibleGroupBox()
        self.local_diagnosis_area_groupbox.setTitle("Available diagnosis")
        self.base_layout.addWidget(self.local_diagnosis_area_groupbox)
        # Layout within the dummy collapsible button
        self.modelsFormLayout = qt.QFormLayout(self.local_diagnosis_area_groupbox)

        # model search
        self.local_diagnosis_area_searchbox = ctk.ctkSearchBox()
        self.modelsFormLayout.addRow("Search:", self.local_diagnosis_area_searchbox)

        # model selector
        self.local_diagnosis_selector_combobox = qt.QComboBox()
        self.modelsFormLayout.addRow("Diagnosis:", self.local_diagnosis_selector_combobox)
        self.populate_local_diagnosis()

        self.local_diagnosis_moreinfo_pushbutton = qt.QPushButton('Press to display')
        self.modelsFormLayout.addRow("Details:", self.local_diagnosis_moreinfo_pushbutton)

    def setup_diagnosis_parameters_area(self):
        # The ctk collapsible group box is the overall container, within which a scrollable area is set.
        # Ctk => Layout => scroll area => dummy widget => form layout => Content from ModelParameters
        parametersCollapsibleButton = ctk.ctkCollapsibleGroupBox()
        parametersCollapsibleButton.setTitle("Diagnosis Parameters")
        self.base_layout.addWidget(parametersCollapsibleButton)

        self.parameters_scrollarea_layout = qt.QHBoxLayout(parametersCollapsibleButton)
        self.parameters_groupbox_scrollarea = qt.QScrollArea()
        self.parameters_groupbox_scrollarea.setVerticalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOn)
        self.parameters_groupbox_scrollarea.setHorizontalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)
        self.parameters_groupbox_scrollarea.setWidgetResizable(True)
        self.parameters_scrollarea_layout.addWidget(self.parameters_groupbox_scrollarea)
        dummy_widget = qt.QWidget()
        self.parameters_groupbox_scrollarea.setWidget(dummy_widget)
        parametersFormLayout = qt.QFormLayout()
        dummy_widget.setLayout(parametersFormLayout)
        self.diagnosis_model_parameters = ModelParameters(dummy_widget)

    def setup_connections(self):
        self.local_diagnosis_area_searchbox.connect("textChanged(QString)", self.on_local_diagnosis_search)
        self.local_diagnosis_selector_combobox.connect('currentIndexChanged(int)', self.on_diagnosis_selection)
        self.local_diagnosis_moreinfo_pushbutton.connect('clicked()', self.on_diagnosis_details_selected)

    def get_existing_digests(self):
        cmd = []
        cmd.append(SharedResources.getInstance().docker_path)
        cmd.append('images')
        cmd.append('--digests')
        # print(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        digest_index = 2
        digests = []
        try:
            while True:
                slicer.app.processEvents()
                line = p.stdout.readline()
                if not line:
                    break
                line = line.split()
                if 'DIGEST' in line:
                    digest_index = line.index('DIGEST')
                else:
                    digests.append(line[digest_index])
        except Exception as e:
            print("Exception: {}".format(e))
        return digests

    def populate_local_diagnosis(self):
        digests = self.get_existing_digests()
        jsonFiles = glob(SharedResources.getInstance().json_local_dir + "/*.json")
        jsonFiles.sort(cmp=lambda x, y: cmp(os.path.basename(x), os.path.basename(y)))
        self.jsonModels = []
        for fname in jsonFiles:
            with open(fname, "r") as fp:
                j = json.load(fp, object_pairs_hook=OrderedDict)

            self.jsonModels.append(j)
            # if j['docker']['digest'] in digests:
            #     self.jsonModels.append(j)
            # else:
            #     os.remove(fname)
        # add all the models listed in the json files
        # print('JSON models: {}'.format(self.jsonModels))
        for idx, j in enumerate(self.jsonModels):
            name = j["name"]
            if 'task' in j and j['task'] == 'Diagnosis':
                self.local_diagnosis_selector_combobox.addItem(name, idx)

    def on_diagnosis_selection(self, index):
        self.diagnosis_model_parameters.destroy()
        if index < 0 or self.local_diagnosis_selector_combobox.count == 0:
            return
        jsonIndex = self.local_diagnosis_selector_combobox.itemData(index)
        json_model = self.jsonModels[jsonIndex]
        self.diagnosis_model_parameters.create(json_model)

        if "briefdescription" in self.jsonModels[jsonIndex]:
            tip = self.jsonModels[jsonIndex]["briefdescription"]
            tip = tip.rstrip()
            self.local_diagnosis_selector_combobox.setToolTip(tip)
        else:
            self.local_diagnosis_selector_combobox.setToolTip("")

        # self.enable_user_interface(True)
        #self.onLocateButton()
        DeepSintefLogic.getInstance().selected_model = self.local_diagnosis_selector_combobox

    def on_local_diagnosis_search(self, search_text):
        self.local_diagnosis_selector_combobox.clear()
        # split text on whitespace of and string search
        searchTextList = search_text.split()
        for idx, j in enumerate(self.jsonModels):
            lname = j["name"].lower()
            if 'task' in j and j['task'] == 'Diagnosis':
                # require all elements in list, to add to select. case insensitive
                if reduce(lambda x, y: x and (lname.find(y.lower()) != -1), [True] + searchTextList):
                    self.local_diagnosis_selector_combobox.addItem(j["name"], idx)

    def on_diagnosis_details_selected(self):
        index = self.local_diagnosis_selector_combobox.currentIndex
        model_json = self.jsonModels[[x['name'] == self.local_diagnosis_selector_combobox.currentText for x in self.jsonModels].index(True)]

        tip = ''
        exhaustive_list = ['owner', 'task', 'organ', 'target', 'modality', 'sequence', 'dataset_description']
        for a in exhaustive_list:
            if a in model_json:
                tip = tip + '\n' + a + ':' + model_json[a]

        popup = qt.QMessageBox()
        popup.setWindowTitle('Exhaustive description for {}'.format(self.local_diagnosis_selector_combobox.currentText))
        popup.setText(tip)
        x = popup.exec_()
