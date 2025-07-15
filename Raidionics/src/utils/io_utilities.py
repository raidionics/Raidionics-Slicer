from __main__ import qt, ctk, slicer, vtk
import urllib3
import subprocess
import shutil
import os
import traceback
import csv
import threading
import hashlib
from typing import List
import json
import datetime
import zipfile
import requests
from email.utils import parsedate_to_datetime, formatdate
import webbrowser
import time
from src.utils.resources import SharedResources


def check_internet_conn():
    http = urllib3.PoolManager(timeout=3.0)
    r = http.request('GET', 'google.com', preload_content=False)
    code = r.status
    r.release_conn()
    if code == 200:
        return True
    else:
        return False

def get_available_cloud_models_list() -> List[List[str]]:
    """
    Collects a csv file from Google Drive, summarizing all available models.

    Returns
    ------
    List of all available models on the cloud, each expressed as a List[str].
    Each model list element corresponds to the following headers: Item,link,dependencies,sum.
    """
    cloud_models_list = []
    #cloud_models_list_url = 'https://github.com/raidionics/Raidionics-models/releases/download/rsv1.1.1/Slicer_cloud_models_list.csv'
    cloud_models_list_url = "https://github.com/raidionics/Raidionics-models/releases/download/v1.3.0-rc/Slicer_cloud_models_list_v13.csv"
    try:
        cloud_models_list_filename = os.path.join(SharedResources.getInstance().json_cloud_dir, 'cloud_models_list.csv')
        headers = {}

        if check_internet_conn():
            response = requests.get(cloud_models_list_url, headers=headers, stream=True)
            response.raise_for_status()
            if response.status_code == requests.codes.ok:
                with open(cloud_models_list_filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1048576):
                        f.write(chunk)

        line_count = 0
        with open(cloud_models_list_filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    cloud_models_list.append(row)
    except Exception as e:
        print('Impossible to access the cloud models list.\n')
        print('{}'.format(traceback.format_exc()))

    return cloud_models_list


def download_cloud_model_thread(selected_model):
    download_cloud_model_thread = threading.Thread(target=download_cloud_model(selected_model))
    download_cloud_model_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
    download_cloud_model_thread.start()


def download_cloud_model(selected_model):
    """
    Legacy, but still needed, model download method (use recursively from within the DownloadWorker thread.
    @TODO. Should be removed and the recursive download should just happen inside the worker.

    Parameters
    ----------
    selected_model: str
        Unique name identifier of the model to be downloaded.

    Returns
    -------
    Boolean to indicate if the download operation succeeded or failed.
    """
    model_url = ''
    model_dependencies = []
    model_checksum = None
    model_config_url = None
    tmp_archive_dir = ''
    success = True
    download_state = False
    extract_state = False
    cloud_models = get_available_cloud_models_list()
    try:
        if not check_internet_conn():
            raise ValueError("No internet access!")
        for model in cloud_models:
            if model[0] == selected_model:
                model_url = model[1]
                model_dependencies = model[2].split(';') if model[2].strip() != '' else []
                model_checksum = model[3]
                model_config_url = model[4]

        model_dest_dir = SharedResources.getInstance().model_path
        json_local_dir = SharedResources.getInstance().json_local_dir
        json_cloud_dir = SharedResources.getInstance().json_cloud_dir
        archive_dl_dest = os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache',
                                       str('_'.join(selected_model.split(']')[:-1]).replace('[', '').replace('/',
                                                                                                             '-'))
                                       + '.zip')
        os.makedirs(os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache'), exist_ok=True)
        headers = {}

        response = requests.get(model_config_url, headers=headers, stream=True)
        response.raise_for_status()

        if response.status_code == requests.codes.ok:
            with open(os.path.join(SharedResources.getInstance().json_local_dir,
                                                '_'.join(selected_model[1:-1].split('][')) + '.json'), "wb") as f:
                for chunk in response.iter_content(chunk_size=1048576):
                    f.write(chunk)

        if not os.path.exists(archive_dl_dest) or hashlib.md5(
                open(archive_dl_dest, 'rb').read()).hexdigest() != model_checksum:
            download_state = True

        if download_state:
            headers = {}

            response = requests.get(model_url, headers=headers, stream=True)
            response.raise_for_status()

            if response.status_code == requests.codes.ok:
                with open(archive_dl_dest, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1048576):
                        f.write(chunk)
                extract_state = True
        else:
            zip_content = zipfile.ZipFile(archive_dl_dest).namelist()
            for f in zip_content:
                if not os.path.exists(os.path.join(model_dest_dir, f)):
                    extract_state = True

        if extract_state:
            with zipfile.ZipFile(archive_dl_dest, 'r') as zip_ref:
                zip_ref.extractall(model_dest_dir)

        # Checking if dependencies are needed, and if they exist already locally
        if len(model_dependencies) > 0:
            for dep in model_dependencies:
                success_dep = download_cloud_model(dep)
                success = success & success_dep
    except Exception as e:
        print('Impossible to download the selected cloud model.\n')
        print('{}'.format(traceback.format_exc()))
        success = False
        if os.path.exists(tmp_archive_dir):
            shutil.rmtree(tmp_archive_dir)
    return success


def check_local_model_for_update(selected_model):
    """
    Compares the existing local model with the remote ones, to identify if a new version is available for download,
    by checking the checksums.


    """
    model_url = ''
    model_dependencies = []
    model_checksum = None
    tmp_archive_dir = ''
    cloud_models = get_available_cloud_models_list()
    download_required = False
    try:
        if not check_internet_conn():
            raise ValueError("No internet access!")
        for model in cloud_models:
            if model[0] == selected_model:
                model_url = model[1]
                model_dependencies = model[2].split(';') if model[2].strip() != '' else []
                model_checksum = model[3]
                break

        model_dest_dir = SharedResources.getInstance().model_path
        json_local_dir = SharedResources.getInstance().json_local_dir
        json_cloud_dir = SharedResources.getInstance().json_cloud_dir
        archive_dl_dest = os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache',
                                       str('_'.join(selected_model.split(']')[:-1]).replace('[', '').replace('/', '-'))
                                       + '.zip')
        download_required = not os.path.exists(archive_dl_dest) or hashlib.md5(open(archive_dl_dest, 'rb').read()).hexdigest() != model_checksum

        # Checking if update in dependencies is needed
        if len(model_dependencies) > 0:
            for dep in model_dependencies:
                download_required_dep = check_local_model_for_update(dep)
                download_required = download_required or download_required_dep
    except Exception as e:
        print('Impossible to check for model update for: {}.\n'.format(selected_model))
        print('{}'.format(traceback.format_exc()))
        download_required = False

    return download_required


def get_available_cloud_rads_list():
    cloud_rads_list = []
    cloud_rads_list_url = "https://github.com/raidionics/Raidionics-models/releases/download/v1.3.0-rc/Slicer_cloud_pipelines_list_v13.csv"
    try:
        cloud_rads_list_filename = os.path.join(SharedResources.getInstance().json_cloud_dir, 'cloud_rads_list.csv')
        if check_internet_conn():
            headers = {}
            response = requests.get(cloud_rads_list_url, headers=headers, stream=True)
            response.raise_for_status()

            if response.status_code == requests.codes.ok:
                with open(cloud_rads_list_filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1048576):
                        f.write(chunk)

        line_count = 0
        with open(cloud_rads_list_filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    cloud_rads_list.append(row)
    except Exception as e:
        print('Impossible to access the cloud rads list.\n')
        print('{}'.format(traceback.format_exc()))

    return cloud_rads_list


def check_local_diagnosis_for_update(selected_diagnosis):
    diagnosis_url = ''
    diagnosis_dependencies = []
    diagnosis_md5sum = None
    diagnosis_pipeline_url = ''
    download_required = False
    cloud_diagnoses = get_available_cloud_rads_list()
    try:
        if not check_internet_conn():
            raise ValueError("No internet access!")
        for diagnosis in cloud_diagnoses:
            if diagnosis[0] == selected_diagnosis:
                diagnosis_url = diagnosis[1]
                diagnosis_dependencies = diagnosis[2].split(';') if diagnosis[2].strip() != '' else []
                diagnosis_md5sum = diagnosis[3]
                diagnosis_pipeline_url = diagnosis[4]

        json_local_dir = SharedResources.getInstance().json_local_dir
        dl_dest = os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache',
                                       str('_'.join(selected_diagnosis.split(']')[:-1]).replace('[', '').replace('/', '-'))
                                       + '.json')

        headers = {}
        response = requests.get(diagnosis_url, headers=headers, stream=True)
        response.raise_for_status()

        if response.status_code == requests.codes.ok:
            with open(dl_dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=1048576):
                    f.write(chunk)

        shutil.copy(src=dl_dest, dst=os.path.join(json_local_dir, os.path.basename(dl_dest)))

        diagnosis_dir = SharedResources.getInstance().diagnosis_path
        dl_dest = os.path.join(diagnosis_dir,
                               str('_'.join(selected_diagnosis.split(']')[:-1]).replace('[', '').replace('/', '-'))
                               + '.json')
        headers = {}
        response = requests.get(diagnosis_pipeline_url, headers=headers, stream=True)
        response.raise_for_status()

        if response.status_code == requests.codes.ok:
            with open(dl_dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=1048576):
                    f.write(chunk)

        # Checking if dependencies must be updated.
        if len(diagnosis_dependencies) > 0:
            for dep in diagnosis_dependencies:
                download_required_dep = check_local_model_for_update(dep)
                download_required = download_required or download_required_dep
    except Exception as e:
        print('Impossible to check update for the selected cloud diagnosis.\n')
        print('{}'.format(traceback.format_exc()))
        download_required = False

    return download_required


class WorkerFinishedSignal(qt.QObject):
    finished_signal = qt.Signal()


class DownloadWorker(qt.QObject): #qt.QThread
    finished_signal = qt.Signal(bool)

    def __init__(self):
        super(qt.QObject, self).__init__()

    def onWorkerStart(self, model=None, diagnosis=None, docker_image=None):
        try:
            if model is not None:
                self.download_cloud_model(model)
            elif diagnosis is not None:
                self.download_cloud_diagnosis(diagnosis)
            elif docker_image is not None:
                self.download_docker_image(docker_image)
        except Exception:
            self.finished_signal.emit(False)

    def download_cloud_model(self, selected_model):
        model_url = ''
        model_dependencies = []
        model_checksum = None
        model_config_url = None
        tmp_archive_dir = ''
        success = True
        download_state = False
        extract_state = False
        cloud_models = get_available_cloud_models_list()
        try:
            if not check_internet_conn():
                raise ValueError("No internet access!")
            for model in cloud_models:
                if model[0] == selected_model:
                    model_url = model[1]
                    model_dependencies = model[2].split(';') if model[2].strip() != '' else []
                    model_checksum = model[3]
                    model_config_url = model[4]

            model_dest_dir = SharedResources.getInstance().model_path
            json_local_dir = SharedResources.getInstance().json_local_dir
            json_cloud_dir = SharedResources.getInstance().json_cloud_dir
            archive_dl_dest = os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache',
                                           str('_'.join(selected_model.split(']')[:-1]).replace('[', '').replace('/',
                                                                                                                 '-'))
                                           + '.zip')
            os.makedirs(os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache'), exist_ok=True)
            headers = {}
            response = requests.get(model_config_url, headers=headers, stream=True)
            response.raise_for_status()
            if response.status_code == requests.codes.ok:
                with open(os.path.join(SharedResources.getInstance().json_local_dir, '_'.join(selected_model[1:-1].split('][')) + '.json'), "wb") as f:
                    for chunk in response.iter_content(chunk_size=1048576):
                        f.write(chunk)

            if not os.path.exists(archive_dl_dest) or hashlib.md5(open(archive_dl_dest, 'rb').read()).hexdigest() != model_checksum:
                download_state = True

            if download_state:
                headers = {}

                response = requests.get(model_url, headers=headers, stream=True)
                response.raise_for_status()

                if response.status_code == requests.codes.ok:
                    with open(archive_dl_dest, "wb") as f:
                        for chunk in response.iter_content(chunk_size=1048576):
                            f.write(chunk)
                    extract_state = True
            else:
                zip_content = zipfile.ZipFile(archive_dl_dest).namelist()
                for f in zip_content:
                    if not os.path.exists(os.path.join(model_dest_dir, f)):
                        extract_state = True

            if extract_state:
                with zipfile.ZipFile(archive_dl_dest, 'r') as zip_ref:
                    zip_ref.extractall(model_dest_dir)

            # Checking if dependencies are needed, and if they exist already locally
            if len(model_dependencies) > 0:
                for dep in model_dependencies:
                    success_dep = download_cloud_model(dep)
                    success = success & success_dep
        except Exception as e:
            print('Impossible to download the selected cloud model.\n')
            print('{}'.format(traceback.format_exc()))
            success = False
            if os.path.exists(tmp_archive_dir):
                shutil.rmtree(tmp_archive_dir)

        self.finished_signal.emit(success)
        # return success

    def download_cloud_diagnosis(self, selected_diagnosis):
        diagnosis_url = ''
        diagnosis_dependencies = []
        diagnosis_md5sum = None
        tmp_archive_dir = ''
        success = True
        cloud_diagnoses = get_available_cloud_rads_list()
        try:
            if not check_internet_conn():
                raise ValueError("No internet access!")
            for diagnosis in cloud_diagnoses:
                if diagnosis[0] == selected_diagnosis:
                    diagnosis_url = diagnosis[1]
                    diagnosis_dependencies = diagnosis[2].split(';') if diagnosis[2].strip() != '' else []
                    diagnosis_md5sum = diagnosis[3]

            json_local_dir = SharedResources.getInstance().json_local_dir
            dl_dest = os.path.join(SharedResources.getInstance().Raidionics_dir, '.cache',
                                   str('_'.join(selected_diagnosis.split(']')[:-1]).replace('[', '').replace('/',
                                                                                                             '-'))
                                   + '.json')
            headers = {}
            response = requests.get(diagnosis_url, headers=headers, stream=True)
            response.raise_for_status()
            if response.status_code == requests.codes.ok:
                with open(dl_dest, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1048576):
                        f.write(chunk)

            shutil.copy(src=dl_dest, dst=os.path.join(json_local_dir, os.path.basename(dl_dest)))

            # Checking if dependencies are needed and if they exist already locally, otherwise triggers a download
            if len(diagnosis_dependencies) > 0:
                for dep in diagnosis_dependencies:
                    success_dep = download_cloud_model(dep)
                    success = success & success_dep
        except Exception as e:
            print('Impossible to download the selected cloud model.\n')
            print('{}'.format(traceback.format_exc()))
            success = False
            if os.path.exists(tmp_archive_dir):
                shutil.rmtree(tmp_archive_dir)
        self.finished_signal.emit(success)
        # return success

    def download_docker_image(self, select_image):
        # @TODO. If the download is slow, no info is printed on screen, might make the user wonder what is happening...
        cmd_docker = ['docker', 'image', 'pull', select_image]
        p = subprocess.Popen(cmd_docker, stdout=subprocess.PIPE)
        res_lines = ""
        while True:
            slicer.app.processEvents()
            line = p.stdout.readline().decode("utf-8")
            if not line:
                break
            res_lines = res_lines + '/n' + line
        # cmd_docker = ['docker', 'image', 'inspect', select_image]
        # p = subprocess.Popen(cmd_docker, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # # res_lines = ""
        # # while True:
        # #     slicer.app.processEvents()
        # #     line = p.stderr.readline().decode("utf-8")
        # #     if not line:
        # #         break
        # #     res_lines = res_lines + '/n' + line
        # #
        # # # If the image could not be downloaded -- abort
        # # if 'Error: No such image' in res_lines:
        # #     result = False
        # # else:
        # #     result = True
        #
        # stdout, stderr = p.communicate()
        # # If the image could not be downloaded -- abort
        # if 'Error: No such image' in stderr.decode("utf-8"):
        #     result = False
        # else:
        #     result = True

        self.finished_signal.emit(True)
