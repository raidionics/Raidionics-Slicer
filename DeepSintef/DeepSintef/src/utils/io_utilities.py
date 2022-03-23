from __main__ import qt, ctk, slicer, vtk

import subprocess
import shutil
import os
import traceback
import csv
import threading
import hashlib
import json
import time
try:
    import gdown
    if int(gdown.__version__.split('.')[0]) < 4 or int(gdown.__version__.split('.')[1]) < 4:
        from __main__ import slicer
        slicer.util.pip_install('gdown==4.4.0')
except:
    from __main__ import slicer
    slicer.util.pip_install('gdown==4.4.0')
    import gdown

from src.utils.resources import SharedResources


def get_available_cloud_models_list():
    cloud_models_list = []
    cloud_models_list_url = 'https://drive.google.com/uc?id=13-Mx1Os9eXB_bJBcJt_o9MXQrRI1xONi'
    try:
        cloud_models_list_filename = os.path.join(SharedResources.getInstance().json_cloud_dir, 'cloud_models_list.csv')
        gdown.cached_download(url=cloud_models_list_url, path=cloud_models_list_filename)
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

    # success = download_cloud_model_thread.join()
    # return success

    # success = False
    # import concurrent.futures
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     future = executor.submit(download_cloud_model, selected_model, local_models, cloud_models)
    #     success = future.result()
    # return success


def download_cloud_model(selected_model):
    model_url = ''
    model_dependencies = []
    model_checksum = None
    tmp_archive_dir = ''
    success = True
    cloud_models = get_available_cloud_models_list()
    try:
        for model in cloud_models:
            if model[0] == selected_model:
                model_url = model[1]
                model_dependencies = model[2].split(';') if model[2].strip() != '' else []
                model_checksum = model[3]

        model_dest_dir = SharedResources.getInstance().model_path
        json_local_dir = SharedResources.getInstance().json_local_dir
        json_cloud_dir = SharedResources.getInstance().json_cloud_dir
        archive_dl_dest = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache',
                                       str('_'.join(selected_model.split(']')[:-1]).replace('[', '').replace('/', '-'))
                                       + '.zip')
        tmp_archive_dir = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache', '.tmp')
        if not os.path.exists(os.path.dirname(archive_dl_dest)):
            os.makedirs(os.path.dirname(archive_dl_dest))

        gdown.cached_download(url=model_url, path=archive_dl_dest, md5=model_checksum)
        extract_state = not os.path.exists(archive_dl_dest) or hashlib.md5(open(archive_dl_dest, 'rb').read()).hexdigest() != model_checksum
        local_headers = []
        for _, _, files in os.walk(json_local_dir):
            for f in files:
                local_headers.append(f)
            break

        missing_header = True
        for loc_h in local_headers:
            json_file = json.load(open(os.path.join(json_local_dir, loc_h), 'rb'))
            if json_file["name"] == selected_model:
                missing_header = False

        extract_state = extract_state or missing_header
        if extract_state:
            os.makedirs(tmp_archive_dir, exist_ok=True)
            gdown.extractall(path=archive_dl_dest, to=tmp_archive_dir)

            model_folder = []
            config_file = []
            for _, dirs, files in os.walk(tmp_archive_dir):
                for d in dirs:
                    model_folder.append(d)
                for f in files:
                    if 'json' in f:
                        config_file.append(f)
                break

            shutil.move(src=os.path.join(tmp_archive_dir, config_file[0]), dst=os.path.join(json_local_dir, config_file[0]))

            if os.path.exists(os.path.join(model_dest_dir, model_folder[0])):
                shutil.rmtree(os.path.join(model_dest_dir, model_folder[0]))
            shutil.move(src=os.path.join(tmp_archive_dir, model_folder[0]), dst=os.path.join(model_dest_dir, model_folder[0]))

            shutil.rmtree(tmp_archive_dir)

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

    :param selected_model:
    :return:
    """
    model_url = ''
    model_dependencies = []
    model_checksum = None
    tmp_archive_dir = ''
    cloud_models = get_available_cloud_models_list()
    download_required = False
    try:
        for model in cloud_models:
            if model[0] == selected_model:
                model_url = model[1]
                model_dependencies = model[2].split(';') if model[2].strip() != '' else []
                model_checksum = model[3]

        model_dest_dir = SharedResources.getInstance().model_path
        json_local_dir = SharedResources.getInstance().json_local_dir
        json_cloud_dir = SharedResources.getInstance().json_cloud_dir
        archive_dl_dest = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache',
                                       str('_'.join(selected_model.split(']')[:-1]).replace('[', '').replace('/', '-'))
                                       + '.zip')
        tmp_archive_dir = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache', '.tmp')
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


def get_available_cloud_diagnoses_list():
    cloud_diagnoses_list = []
    cloud_diagnoses_list_url = 'https://drive.google.com/uc?id=1FDleimGDdODufCaTqGdK4yTVA9JdOAHx'
    try:
        cloud_diagnoses_list_filename = os.path.join(SharedResources.getInstance().json_cloud_dir, 'cloud_diagnoses_list.csv')
        gdown.cached_download(url=cloud_diagnoses_list_url, path=cloud_diagnoses_list_filename)
        line_count = 0
        with open(cloud_diagnoses_list_filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    cloud_diagnoses_list.append(row)
    except Exception as e:
        print('Impossible to access the cloud diagnoses list.\n')
        print('{}'.format(traceback.format_exc()))

    return cloud_diagnoses_list


def check_local_diagnosis_for_update(selected_diagnosis):
    diagnosis_url = ''
    diagnosis_dependencies = []
    diagnosis_checksum = None
    download_required = False
    cloud_diagnoses = get_available_cloud_diagnoses_list()
    try:
        for diagnosis in cloud_diagnoses:
            if diagnosis[0] == selected_diagnosis:
                diagnosis_url = diagnosis[1]
                diagnosis_dependencies = diagnosis[2].split(';') if diagnosis[2].strip() != '' else []
                diagnosis_checksum = diagnosis[3]

        json_local_dir = SharedResources.getInstance().json_local_dir
        dl_dest = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache',
                                       str('_'.join(selected_diagnosis.split(']')[:-1]).replace('[', '').replace('/', '-'))
                                       + '.json')
        gdown.cached_download(url=diagnosis_url, path=dl_dest, md5=diagnosis_checksum)
        shutil.copy(src=dl_dest, dst=os.path.join(json_local_dir, os.path.basename(dl_dest)))

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


def download_cloud_diagnosis(selected_diagnosis):
    diagnosis_url = ''
    diagnosis_dependencies = []
    diagnosis_checksum = None
    tmp_archive_dir = ''
    success = True
    cloud_diagnoses = get_available_cloud_diagnoses_list()
    try:
        for diagnosis in cloud_diagnoses:
            if diagnosis[0] == selected_diagnosis:
                diagnosis_url = diagnosis[1]
                diagnosis_dependencies = diagnosis[2].split(';') if diagnosis[2].strip() != '' else []
                diagnosis_checksum = diagnosis[3]

        json_local_dir = SharedResources.getInstance().json_local_dir
        dl_dest = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache',
                                       str('_'.join(selected_diagnosis.split(']')[:-1]).replace('[', '').replace('/', '-'))
                                       + '.json')
        gdown.cached_download(url=diagnosis_url, path=dl_dest, md5=diagnosis_checksum)
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
    return success


class WorkerFinishedSignal(qt.QObject):
    finished_signal = qt.Signal()


class DownloadWorker(qt.QObject): #qt.QThread
    def __init__(self):
        self.finished_signal = WorkerFinishedSignal() #qt.Signal() #qt.Signal(name='workerFinished')

    def onWorkerStart(self, model=None, diagnosis=None, docker_image=None):
        if model is not None:
            self.download_cloud_model2(model)
        elif diagnosis is not None:
            self.download_cloud_diagnosis2(diagnosis)
        elif docker_image is not None:
            self.download_docker_image(docker_image)

    def download_cloud_model2(self, selected_model):
        model_url = ''
        model_dependencies = []
        model_checksum = None
        tmp_archive_dir = ''
        success = True
        cloud_models = get_available_cloud_models_list()
        try:
            for model in cloud_models:
                if model[0] == selected_model:
                    model_url = model[1]
                    model_dependencies = model[2].split(';') if model[2].strip() != '' else []
                    model_checksum = model[3]

            model_dest_dir = SharedResources.getInstance().model_path
            json_local_dir = SharedResources.getInstance().json_local_dir
            json_cloud_dir = SharedResources.getInstance().json_cloud_dir
            archive_dl_dest = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache',
                                           str('_'.join(selected_model.split(']')[:-1]).replace('[', '').replace('/',
                                                                                                                 '-'))
                                           + '.zip')
            tmp_archive_dir = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache', '.tmp')
            if not os.path.exists(os.path.dirname(archive_dl_dest)):
                os.makedirs(os.path.dirname(archive_dl_dest))

            gdown.cached_download(url=model_url, path=archive_dl_dest, md5=model_checksum)
            extract_state = not os.path.exists(archive_dl_dest) or hashlib.md5(
                open(archive_dl_dest, 'rb').read()).hexdigest() != model_checksum
            local_headers = []
            for _, _, files in os.walk(json_local_dir):
                for f in files:
                    local_headers.append(f)
                break

            missing_header = True
            for loc_h in local_headers:
                json_file = json.load(open(os.path.join(json_local_dir, loc_h), 'rb'))
                if json_file["name"] == selected_model:
                    missing_header = False

            extract_state = extract_state or missing_header
            if extract_state:
                os.makedirs(tmp_archive_dir, exist_ok=True)
                gdown.extractall(path=archive_dl_dest, to=tmp_archive_dir)

                model_folder = []
                config_file = []
                for _, dirs, files in os.walk(tmp_archive_dir):
                    for d in dirs:
                        model_folder.append(d)
                    for f in files:
                        if 'json' in f:
                            config_file.append(f)
                    break

                shutil.move(src=os.path.join(tmp_archive_dir, config_file[0]),
                            dst=os.path.join(json_local_dir, config_file[0]))

                if os.path.exists(os.path.join(model_dest_dir, model_folder[0])):
                    shutil.rmtree(os.path.join(model_dest_dir, model_folder[0]))
                shutil.move(src=os.path.join(tmp_archive_dir, model_folder[0]),
                            dst=os.path.join(model_dest_dir, model_folder[0]))

                shutil.rmtree(tmp_archive_dir)

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

        self.finished_signal.finished_signal.emit()
        # return success

    def download_cloud_diagnosis2(self, selected_diagnosis):
        diagnosis_url = ''
        diagnosis_dependencies = []
        diagnosis_checksum = None
        tmp_archive_dir = ''
        success = True
        cloud_diagnoses = get_available_cloud_diagnoses_list()
        try:
            for diagnosis in cloud_diagnoses:
                if diagnosis[0] == selected_diagnosis:
                    diagnosis_url = diagnosis[1]
                    diagnosis_dependencies = diagnosis[2].split(';') if diagnosis[2].strip() != '' else []
                    diagnosis_checksum = diagnosis[3]

            json_local_dir = SharedResources.getInstance().json_local_dir
            dl_dest = os.path.join(SharedResources.getInstance().deepsintef_dir, '.cache',
                                   str('_'.join(selected_diagnosis.split(']')[:-1]).replace('[', '').replace('/', '-'))
                                   + '.json')
            gdown.cached_download(url=diagnosis_url, path=dl_dest, md5=diagnosis_checksum)
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
        self.finished_signal.finished_signal.emit()
        # return success

    def download_docker_image(self, select_image):
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

        self.finished_signal.finished_signal.emit()
