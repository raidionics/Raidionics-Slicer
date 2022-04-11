# Raidionics 3D Slicer plugin 
Plugin developed to perform automatic segmentation and clinical reporting using custom models.

Please cite the following article if you use the plugin:  
>`@misc{,`  
      `title=,`  
      `author=,`  
      `year=,`  
      `eprint=,`  
      `primaryClass=`  
`}`

## 1. Method background

More information about the different models provided and architectures used can be accessed from those previous publications:  

>`@article{bouget2021mediastinal,`  
  `title={Mediastinal lymph nodes segmentation using 3D convolutional neural network ensembles and anatomical priors guiding},`  
  `author={Bouget, David and Pedersen, Andr{\'e} and Vanel, Johanna and Leira, Haakon O and Lang{\o}, Thomas},`  
  `journal={arXiv preprint arXiv:2102.06515},`  
  `year={2021}`  
`}`  

## 2. Plugin installation

2.1 Download 3DSlicer for your running Operating System at https://download.slicer.org/ (running on stable 4.11).  

2.2 Download the Raidionics plugin code:  
* release candidate with name .... on the right-hand panel (Github repo).  
* (Or git clone --single-branch --branch master https://github.com/dbouget/Slicer-Raidionics.git /path/to/folder/).  

2.3 Load the plugin into 3DSlicer:   
	∘ All Modules > Extension Wizard.  
	∘ (Slicer v4.11) Developer Tools > Extension Wizard.  
	∘ Select Extension > point to the folder and add it to the path (tick the small box at the bottom).  
A restart of 3DSlicer is necessary after the initial launch with the plugin to have the proper Python environment.  

:warning: old trick necessary for 3DSlicer using Python 2.7  
Install python package inside 3DSlicer
Open 3D Slicer and open the python interaction window.
import pip (if it doesn't work => from pip._internal import main as pipmain)
pip.main(['install', 'package_name']) or pipmain(['install', 'package_name'])

2.4  Plugin use  
The plugin can be found in the Modules drop-down list, inside the 'Machine Learning' category. 

## 3. Docker setup
A proper Docker setup is **mandatory** since all processing is performed within
a Docker image, 3DSlicer is only used for its GUI.  
Start by downloading the Docker Desktop app at https://www.docker.com/products/docker-desktop/.
Then click on the downloaded executable and follow the instructions.  

### 3.1 Ubuntu installation: 
* https://docs.docker.com/install/linux/docker-ce/ubuntu/  
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

### 3.2 Setup the Docker images
• All used Docker images are public, therefore an account is not necessary. 
All images will be automatically downloaded upon model selection.  

## 4. Options
• A global option should be ticked to check for models update.  

