# Custom 3D Slicer plugin to perform segmentation and diagnosis using in-house models

## 1. Plugin installation

• Download 3DSlicer.  
• git clone --single-branch --branch full_update https://github.com/dbouget/Slicer-DeepSintef.git /path/to/folder/
(or clone the base repository and then git checkout the branch.)  
• Install DeepSintef Module:  
	∘ Download locally the module from github.  
	∘ All Modules > Extension Wizard.  
	∘ (Slicer v4.11) Developer Tools > Extension Wizard.  
	∘ Select Extension > point to the folder and add it to the path (tick the small box at the bottom).  
A restart of 3DSlicer is necessary after the initial launch with the plugin to have the proper Python environment.  
:warning: old trick necessary for 3D Slicer using Python 2.7  
Install python package inside 3D Slicer
Open 3D Slicer and open the python interaction window.
import pip (if it doesn't work => from pip._internal import main as pipmain)
pip.main(['install', 'package_name']) or pipmain(['install', 'package_name'])

## 2. Docker setup
A proper Docker setup is **mandatory** since all processing is performed within
a Docker image, 3D Slicer is only used for its GUI.  

### 2.1 Install docker: 
* Ubuntu: https://docs.docker.com/install/linux/docker-ce/ubuntu/  
    > ‣ sudo apt-get update  
    > ‣ sudo apt-get install \  
            apt-transport-https \   
            ca-certificates \  
            curl \  
            gnupg-agent \   
            software-properties-common   
    > ‣ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -   
    > ‣ sudo apt-key fingerprint 0EBFCD88   
    > ‣ sudo apt-get install docker-ce docker-ce-cli containerd.io  
* Visit the Docker website and download the Docker desktop app.  
* 
### 2.2 Setup the Docker image
• Docker images are public, an account is not necessary.

## 3. Models
• A global option should be ticked to check for models update.  

