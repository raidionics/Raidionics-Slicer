import shutil
import os
import traceback
import csv
import threading

try:
    import gdown
except:
    from __main__ import slicer
    slicer.util.pip_install('gdown')
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


def download_cloud_model(selected_model, local_models, cloud_models):
    model_url = ''
    model_dependencies = []
    success = True
    try:
        for model in cloud_models:
            if model[0] == selected_model:
                model_url = model[1]
                model_dependencies = model[2].split(';') if model[2] != '' else []

        model_dest_dir = SharedResources.getInstance().model_path
        json_local_dir = SharedResources.getInstance().json_local_dir
        json_cloud_dir = SharedResources.getInstance().json_cloud_dir
        archive_dl_dest = os.path.join(json_cloud_dir, 'archive.zip')
        gdown.cached_download(url=model_url, path=archive_dl_dest)  # , md5=md5
        gdown.extractall(path=archive_dl_dest, to=json_cloud_dir)

        model_folder = []
        config_file = []
        for _, dirs, files in os.walk(json_cloud_dir):
            for d in dirs:
                model_folder.append(d)
            for f in files:
                if 'json' in f:
                    config_file.append(f)
            break

        shutil.move(src=os.path.join(json_cloud_dir, config_file[0]), dst=os.path.join(json_local_dir, config_file[0]))
        shutil.move(src=os.path.join(json_cloud_dir, model_folder[0]), dst=os.path.join(model_dest_dir, model_folder[0]))
        os.remove(archive_dl_dest)

        # Checking if dependencies are needed, and if they exist already locally
        if len(model_dependencies) > 0:
            for dep in model_dependencies:
                already_local = True if True in [x["name"] == dep for x in self.jsonModels] else False
                if not already_local:
                    success_dep = download_cloud_model(dep, local_models, cloud_models)
                    success = success & success_dep
    except Exception as e:
        success = False

    return success
