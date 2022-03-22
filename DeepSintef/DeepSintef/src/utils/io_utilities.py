import shutil
import os
import traceback
import csv
import threading
import hashlib
import json
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


def download_cloud_model_thread(selected_model, local_models, cloud_models):
    download_cloud_model_thread = threading.Thread(target=download_cloud_model(selected_model, local_models, cloud_models))
    download_cloud_model_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
    download_cloud_model_thread.start()
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


# def check_for_local_model_update(selected_model, local_models):
#     """
#
#     :param selected_model:
#     :param local_models:
#     :return:
#     """
#     for model in local_models_models:
#         if model[0] == selected_model:
#             model_url = model[1]
#             model_dependencies = model[2].split(';') if model[2].strip() != '' else []
#             model_checksum = model[3]
#
#     models_archive_path = os.path.join(expanduser('~'), '.neurorads', 'resources', 'models',
#                                        '.cache', model_name + '.zip')
#     os.makedirs(os.path.dirname(models_archive_path), exist_ok=True)
#     gdown.cached_download(url=url, path=models_archive_path, md5=md5)


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
