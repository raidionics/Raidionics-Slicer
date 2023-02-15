from __main__ import qt, ctk, slicer, vtk
import threading
from src.utils.io_utilities import download_cloud_model, download_cloud_model_thread, download_cloud_diagnosis,\
    DownloadWorker


class DownloadDialog(qt.QDialog):

    def __init__(self, parent=None):
        super(qt.QDialog, self).__init__(parent)
        self.model_name = None
        self.diagnosis_name = None
        self.docker_image_name = None
        self.base_layout = qt.QGridLayout()
        self.download_label = qt.QLabel('New model to download.')
        self.base_layout.addWidget(self.download_label, 0, 0)
        self.start_download_pushbutton = qt.QPushButton('Download')
        # self.start_download_pushbutton.setCheckable(False)
        self.start_download_pushbuttonbox = qt.QDialogButtonBox()
        self.start_download_pushbuttonbox.addButton(self.start_download_pushbutton, qt.QDialogButtonBox.ActionRole)
        # self.start_download_pushbuttonbox = qt.QDialogButtonBox(qt.QDialogButtonBox.Yes)
        self.base_layout.addWidget(self.start_download_pushbuttonbox, 0, 1)

        # self.base_layout.addWidget(self.select_tumor_type_combobox, 0, 1)
        # self.exit_accept_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Ok)
        # self.base_layout.addWidget(self.exit_accept_pushbutton, 1, 0)
        # self.exit_cancel_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Cancel)
        # self.base_layout.addWidget(self.exit_cancel_pushbutton, 1, 1)

        self.setLayout(self.base_layout)

        self.worker = DownloadWorker()
        self.worker.finished_signal.connect(self.on_worker_finished)

        # self.start_download_pushbutton.clicked.connect(self.on_worker_started())
        self.start_download_pushbuttonbox.clicked.connect(self.on_button_pressed)

        # self.select_tumor_type_combobox.currentTextChanged.connect(self.on_type_selected)
        # self.exit_accept_pushbutton.accepted.connect(self.accept)
        # self.exit_cancel_pushbutton.rejected.connect(self.reject)

    # def my_exec(self, model=None, diagnosis=None):
    #     self.worker.onWorkerStart(model=model, diagnosis=diagnosis)
    #     self.exec()
        # success = download_cloud_model(model)
        # self.accept()
    # def on_type_selected(self, text):
    #     SharedResources.getInstance().user_diagnosis_configuration['Neuro']['tumor_type'] = text

    def set_model_name(self, model_name):
        self.model_name = model_name
        self.download_label.setText("New model available for: {}".format(model_name))
        slicer.app.processEvents()

    def set_diagnosis_name(self, diagnosis_name):
        self.diagnosis_name = diagnosis_name
        self.download_label.setText("New RADS available for: {}".format(diagnosis_name))
        slicer.app.processEvents()

    def set_docker_image_name(self, docker_image_name):
        self.docker_image_name = docker_image_name
        self.download_label.setText("New docker image available for: {}".format(docker_image_name))
        slicer.app.processEvents()

    def on_button_pressed(self, button):
        if button.text == "Download":
            self.on_worker_started()

    def on_worker_started(self):
        if self.model_name is not None or self.diagnosis_name is not None or self.docker_image_name is not None:
            self.download_label.setText("Downloading, please wait ...")
            self.start_download_pushbutton.setEnabled(False)
            slicer.app.processEvents()
            self.worker.onWorkerStart(model=self.model_name, diagnosis=self.diagnosis_name,
                                      docker_image=self.docker_image_name)

    def on_worker_finished(self, success_state):
        if success_state:
            self.accept()
        else:
            self.download_label.setText("Downloading failed.")
            # @TODO. Should then pop-up a browser window with the model url, let the user download it manually,
            # then ask where the archive has been saved, and perform its extraction...
