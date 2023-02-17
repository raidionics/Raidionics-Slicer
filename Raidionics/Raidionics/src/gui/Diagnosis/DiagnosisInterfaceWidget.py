from __main__ import qt, ctk, slicer, vtk
from glob import glob
import os
import json
from collections import OrderedDict
import subprocess
import sys
if sys.version_info.major == 3:
    from functools import reduce

from src.utils.resources import SharedResources
from src.logic.model_parameters import *
from src.RaidionicsLogic import RaidionicsLogic
from src.utils.io_utilities import get_available_cloud_diagnoses_list, download_cloud_diagnosis, check_local_diagnosis_for_update
from src.gui.UtilsWidgets.DownloadDialog import DownloadDialog


class DiagnosisInterfaceWidget(qt.QWidget):
    """
    GUI component displaying the selection of possible diagnosis available, very similar to the segmentation counter-part.
    """
    diagnosis_available_signal = qt.Signal(bool)

    def __init__(self, parent=None):
        super(DiagnosisInterfaceWidget, self).__init__(parent)
        self.base_layout = qt.QVBoxLayout()
        self.setup_cloud_diagnosis_area()
        self.setup_local_diagnosis_area()
        # self.populate_local_diagnosis()
        # self.populate_cloud_diagnosis()
        self.setup_diagnosis_parameters_area()
        self.setLayout(self.base_layout)
        self.setup_connections()
        # self.on_diagnosis_selection(0)
        self.json_diagnoses = []
        self.populate_local_diagnosis()
        self.populate_cloud_diagnosis()

    def setup_cloud_diagnosis_area(self):
        self.cloud_diagnosis_area_groupbox = ctk.ctkCollapsibleGroupBox()
        self.cloud_diagnosis_area_groupbox.setTitle("Available cloud RADS")
        self.base_layout.addWidget(self.cloud_diagnosis_area_groupbox)
        # Layout within the dummy collapsible button
        self.cloud_diagnosis_area_groupbox_layout = qt.QFormLayout(self.cloud_diagnosis_area_groupbox)

        # model search
        self.cloud_diagnosis_area_searchbox = ctk.ctkSearchBox()
        self.cloud_diagnosis_area_groupbox_layout.addRow("Search:", self.cloud_diagnosis_area_searchbox)

        # model selector
        self.cloud_diagnosis_selector_combobox = qt.QComboBox()
        self.cloud_diagnosis_area_groupbox_layout.addRow("RADS:", self.cloud_diagnosis_selector_combobox)

        self.cloud_diagnosis_download_pushbutton = qt.QPushButton('Press to download')
        self.cloud_diagnosis_area_groupbox_layout.addRow("Download:", self.cloud_diagnosis_download_pushbutton)
        self.cloud_diagnosis_download_pushbutton.setEnabled(False)

    def setup_local_diagnosis_area(self):
        self.local_diagnosis_area_groupbox = ctk.ctkCollapsibleGroupBox()
        self.local_diagnosis_area_groupbox.setTitle("Local RADS")
        self.base_layout.addWidget(self.local_diagnosis_area_groupbox)
        # Layout within the dummy collapsible button
        self.modelsFormLayout = qt.QFormLayout(self.local_diagnosis_area_groupbox)

        # model search
        self.local_diagnosis_area_searchbox = ctk.ctkSearchBox()
        self.modelsFormLayout.addRow("Search:", self.local_diagnosis_area_searchbox)

        # model selector
        self.local_diagnosis_selector_combobox = qt.QComboBox()
        self.modelsFormLayout.addRow("RADS:", self.local_diagnosis_selector_combobox)

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
        self.cloud_diagnosis_download_pushbutton.clicked.connect(self.on_cloud_diagnosis_download_selected)

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

    def populate_cloud_diagnosis(self):
        self.cloud_diagnosis_list = []
        self.cloud_diagnosis_selector_combobox.clear()
        cloud_diagnosis_list = get_available_cloud_diagnoses_list()
        for idx, model in enumerate(cloud_diagnosis_list):
            already_local = True if True in [x["name"] == model[0] for x in self.json_diagnoses] else False
            if not already_local:
                self.cloud_diagnosis_list.append(model)
                self.cloud_diagnosis_selector_combobox.addItem(model[0], idx)

        if len(self.cloud_diagnosis_list) >= 1:
            self.cloud_diagnosis_download_pushbutton.setEnabled(True)
        else:
            self.cloud_diagnosis_download_pushbutton.setEnabled(False)

    def populate_local_diagnosis(self):
        self.local_diagnosis_selector_combobox.clear()
        self.local_diagnosis_selector_combobox.addItem("", 0)
        jsonFiles = glob(SharedResources.getInstance().json_local_dir + "/*.json")
        jsonFiles = sorted(jsonFiles)
        self.json_diagnoses = []
        for fname in jsonFiles:
            if 'Diagnosis' in fname:
                with open(fname, "r") as fp:
                    j = json.load(fp, object_pairs_hook=OrderedDict)

                self.json_diagnoses.append(j)
        for idx, j in enumerate(self.json_diagnoses):
            name = j["name"]
            if 'task' in j and j['task'] == 'Diagnosis':
                self.local_diagnosis_selector_combobox.addItem(name, idx + 1)

    def on_diagnosis_selection(self, index):
        selected_model = self.local_diagnosis_selector_combobox.currentText
        selected_diagnosis = self.local_diagnosis_selector_combobox.currentText
        if SharedResources.getInstance().global_active_model_update:
            dl_req = check_local_diagnosis_for_update(selected_diagnosis)
            if dl_req:
                diag = DownloadDialog(self)
                diag.set_diagnosis_name(selected_diagnosis)
                diag.exec()

        self.diagnosis_model_parameters.destroy()
        json_model = self.find_json_model(selected_model_name=selected_model)
        self.diagnosis_model_parameters.create(json_model)

        if "briefdescription" in json_model:
            tip = json_model["briefdescription"]
            tip = tip.rstrip()
            self.local_diagnosis_selector_combobox.setToolTip(tip)
        else:
            self.local_diagnosis_selector_combobox.setToolTip("")

        # self.enable_user_interface(True)
        #self.onLocateButton()
        RaidionicsLogic.getInstance().selected_model = self.local_diagnosis_selector_combobox
        docker_status = RaidionicsLogic.getInstance().check_docker_image_local_existence(self.diagnosis_model_parameters.dockerImageName)
        if not docker_status:
            diag = DownloadDialog(self)
            diag.set_docker_image_name(self.diagnosis_model_parameters.dockerImageName)
            diag.exec()
            new_docker_status = RaidionicsLogic.getInstance().check_docker_image_local_existence(self.diagnosis_model_parameters.dockerImageName)
            if new_docker_status:
                self.diagnosis_available_signal.emit(True)
            else:
                tip = 'The required Docker image could not be downloaded, because of inadequet access rights or missing Docker installation.\n'
                tip += '   * Open the command line editor (On Windows, type \'cmd\' in the search bar.)\n'
                tip += '   * Copy and execute: docker image pull {}\n'.format(self.model_parameters.dockerImageName)
                tip += '   * Wait for the download to be complete, then exit the popup.\n'
                popup = qt.QMessageBox()
                popup.setWindowTitle('Warning')
                popup.setText(tip)
                x = popup.exec_()
                self.diagnosis_available_signal.emit(False)
        else:
            self.diagnosis_available_signal.emit(True)

    def on_local_diagnosis_search(self, search_text):
        self.local_diagnosis_selector_combobox.clear()
        # split text on whitespace of and string search
        searchTextList = search_text.split()
        for idx, j in enumerate(self.json_diagnoses):
            lname = j["name"].lower()
            if 'task' in j and j['task'] == 'Diagnosis':
                # require all elements in list, to add to select. case insensitive
                if reduce(lambda x, y: x and (lname.find(y.lower()) != -1), [True] + searchTextList):
                    self.local_diagnosis_selector_combobox.addItem(j["name"], idx)

    def on_diagnosis_details_selected(self):
        index = self.local_diagnosis_selector_combobox.currentIndex
        model_json = self.json_diagnoses[[x['name'] == self.local_diagnosis_selector_combobox.currentText for x in self.json_diagnoses].index(True)]

        tip = ''
        exhaustive_list = ['owner', 'task', 'organ', 'target', 'modality', 'sequence', 'dataset_description']
        for a in exhaustive_list:
            if a in model_json:
                tip = tip + '\n' + a + ':' + model_json[a]

        popup = qt.QMessageBox()
        popup.setWindowTitle('Exhaustive description for {}'.format(self.local_diagnosis_selector_combobox.currentText))
        popup.setText(tip)
        x = popup.exec_()

    def on_cloud_diagnosis_download_selected(self):
        # @TODO. Not ideal as it requires to click twice on download, but at least it will hang
        # during pop-up time, should be more understandable for the user.
        digests = self.get_existing_digests()
        selected_diagnosis = self.cloud_diagnosis_selector_combobox.currentText
        diag = DownloadDialog(self)
        diag.set_diagnosis_name(selected_diagnosis)
        diag.exec()
        # success = download_cloud_diagnosis(selected_diagnosis)
        # if True: #success:
        self.populate_local_diagnosis()
        self.populate_cloud_diagnosis()

    def find_json_model(self, selected_model_name):
        json_model = None
        for m in self.json_diagnoses:
            if m['name'] == selected_model_name:
                json_model = m
                break
        return json_model
