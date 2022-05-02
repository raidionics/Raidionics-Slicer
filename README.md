# Raidionics 3D Slicer plugin 
Plugin developed to perform automatic segmentation and clinical reporting (RADS) using custom models.

## 1. Methodological background

More information about the different models provided and architectures used can be accessed from the below-listed publications.  

## 1.1 Neuro  
* AGUNet neural network architecture => [Meningioma Segmentation in T1-Weighted MRI Leveraging Global Context and Attention Mechanisms](https://www.frontiersin.org/articles/10.3389/fradi.2021.711514/full)

* Standardized reporting and Data System (RADS) => [Glioblastoma Surgery Imaging—Reporting and Data System: Standardized Reporting of Tumor Volume, Location, and Resectability Based on Automated Segmentations ](https://www.mdpi.com/2072-6694/13/12/2854)

* Segmentation performance => [Glioblastoma Surgery Imaging–Reporting and Data System: Validation and Performance of the Automated Segmentation Task ](https://www.mdpi.com/2072-6694/13/18/4674)

## 1.2 Mediastinum
* Mediastinum organs segmentation => [Semantic segmentation and detection of mediastinal lymph nodes and anatomical structures in CT data for lung cancer staging](https://link.springer.com/article/10.1007/s11548-019-01948-8)  
* Lymph nodes segmentation => [Mediastinal lymph nodes segmentation using 3D convolutional neural network ensembles and anatomical priors guiding](https://www.tandfonline.com/doi/pdf/10.1080/21681163.2022.2043778)


## 2. Plugin installation

2.1 Download 3DSlicer for your running Operating System at https://download.slicer.org/ (running on stable 4.11).  

2.2 Download the Raidionics plugin code:  
* release candidate with name Raidionics-Slicer on the right-hand panel (Github repo).  
Or
* git clone --single-branch --branch master https://github.com/dbouget/Raidionics-Slicer.git /path/to/folder/.  

2.3 Download and install Docker (see Section 3).  

2.3 Load the plugin into 3DSlicer:   
	∘ All Modules > Extension Wizard.  
	∘ (Slicer v4.11) Developer Tools > Extension Wizard.  
	∘ Select Extension > point to the folder (second Raidionics) and add it to the path (tick the small box at the bottom).  
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
All images will be automatically downloaded upon model selection, which might 
take some minutes while the 3DSlicer interface won't be responding.  

• When you execute for the first time, you might get a pop-up from Docker asking to allow
the sharing of a .raidonics-slicer directory, accept!

## 4. Options
• A global option should be ticked to check for models update.

### How to cite
Please cite the following article if you use the plugin:
```
@misc{https://doi.org/10.48550/arxiv.2204.14199,
title = {Preoperative brain tumor imaging: models and software for segmentation and standardized reporting},
author = {Bouget, D. and Pedersen, A. and Jakola, A. S. and Kavouridis, V. and Emblem, K. E. and Eijgelaar, R. S. and Kommers, I. and Ardon, H. and Barkhof, F. and Bello, L. and Berger, M. S. and Nibali, M. C. and Furtner, J. and Hervey-Jumper, S. and Idema, A. J. S. and Kiesel, B. and Kloet, A. and Mandonnet, E. and Müller, D. M. J. and Robe, P. A. and Rossi, M. and Sciortino, T. and Brink, W. Van den and Wagemakers, M. and Widhalm, G. and Witte, M. G. and Zwinderman, A. H. and Hamer, P. C. De Witt and Solheim, O. and Reinertsen, I.},
doi = {10.48550/ARXIV.2204.14199},
url = {https://arxiv.org/abs/2204.14199},
keywords = {Image and Video Processing (eess.IV), Computer Vision and Pattern Recognition (cs.CV), Machine Learning (cs.LG), FOS: Electrical engineering, electronic engineering, information engineering, FOS: Electrical engineering, electronic engineering, information engineering, FOS: Computer and information sciences, FOS: Computer and information sciences, I.4.6; J.3},
publisher = {arXiv},
year = {2022},
copyright = {Creative Commons Attribution 4.0 International}}
```

