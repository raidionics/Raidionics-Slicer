# Raidionics-Slicer
Plugin for 3D Slicer to use the segmentation models and clinical reporting techniques (RADS) packaged in Raidionics.
The plugin was first introduced in the article _"Brain tumor preoperative surgery imaging: models and software solutions for
segmentation and standardized reporting"_, published in [Frontiers in Neurology](https://www.frontiersin.org/articles/10.3389/fneur.2022.932219/full).  

<p align="center">
<img src="Raidionics/Raidionics/Resources/Icons/Raidionics-Slicer.gif" width="85%">
</p>

<details open>
<summary>

## Installation
</summary>

The plugin has been tested with the stable release 5.2.1 of 3D Slicer.

* Download 3D Slicer for your running operating system from [here](https://download.slicer.org/).

* Download the plugin source code through one of:  
    ∘ Downloading stable release from [here](https://github.com/dbouget/Raidionics-Slicer/releases).  
    ∘ Cloning current state: `git clone --single-branch --branch master https://github.com/dbouget/Raidionics-Slicer.git`

* Download and install Docker (see below).

* Load the plugin into 3D Slicer:  
	∘ All Modules > Extension Wizard.  
	∘ Developer Tools > Extension Wizard.  
	∘ Select Extension > point to the folder (second Raidionics) and add it to the path (tick the small box at the bottom).

* Restart 3D Slicer to setup Python environment.

</details>

<details open>
<summary>

## How to cite </summary>
If you are using Raidionics-Slicer in your research, please use the following citation:  

```
@article{10.3389/fneur.2022.932219,
    title={Preoperative Brain Tumor Imaging: Models and Software for Segmentation and Standardized Reporting},
    author={Bouget, David and Pedersen, André and Jakola, Asgeir S. and Kavouridis, Vasileios and Emblem, Kyrre E. and Eijgelaar, Roelant S. and Kommers, Ivar and Ardon, Hilko and Barkhof, Frederik and Bello, Lorenzo and Berger, Mitchel S. and Conti Nibali, Marco and Furtner, Julia and Hervey-Jumper, Shawn and Idema, Albert J. S. and Kiesel, Barbara and Kloet, Alfred and Mandonnet, Emmanuel and Müller, Domenique M. J. and Robe, Pierre A. and Rossi, Marco and Sciortino, Tommaso and Van den Brink, Wimar A. and Wagemakers, Michiel and Widhalm, Georg and Witte, Marnix G. and Zwinderman, Aeilko H. and De Witt Hamer, Philip C. and Solheim, Ole and Reinertsen, Ingerid},
    journal={Frontiers in Neurology},
    volume={13},
    year={2022},
    url={https://www.frontiersin.org/articles/10.3389/fneur.2022.932219},
    doi={10.3389/fneur.2022.932219},
    issn={1664-2295}
}
```
</details>

<details>
<summary>

## Methodological background </summary>

More information about the different models provided and architectures used can be accessed from the below-listed publications.  

### Neuro  
* AGU-Net neural network architecture => [Meningioma Segmentation in T1-Weighted MRI Leveraging Global Context and Attention Mechanisms](https://www.frontiersin.org/articles/10.3389/fradi.2021.711514/full)

* Standardized reporting and Data System => [Glioblastoma Surgery Imaging—Reporting and Data System: Standardized Reporting of Tumor Volume, Location, and Resectability Based on Automated Segmentations ](https://www.mdpi.com/2072-6694/13/12/2854)

* Segmentation performance => [Glioblastoma Surgery Imaging–Reporting and Data System: Validation and Performance of the Automated Segmentation Task ](https://www.mdpi.com/2072-6694/13/18/4674)

### Mediastinum
* Mediastinum organs segmentation => [Semantic segmentation and detection of mediastinal lymph nodes and anatomical structures in CT data for lung cancer staging](https://link.springer.com/article/10.1007/s11548-019-01948-8)  
* Lymph nodes segmentation => [Mediastinal lymph nodes segmentation using 3D convolutional neural network ensembles and anatomical priors guiding](https://www.tandfonline.com/doi/pdf/10.1080/21681163.2022.2043778)

</details>

<details>
<summary>

## Docker setup  </summary>  
A proper Docker setup is **mandatory** since all processing is performed within
a Docker image. 3D Slicer is only used for its graphical user interface.  
Start by downloading the Docker Desktop app at https://www.docker.com/products/docker-desktop/.
Then click on the downloaded executable and follow the instructions.  

### Ubuntu installation: 
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

### Setup the Docker images
• The necessary Docker images are public, therefore an account is not necessary. 
All images will be automatically downloaded upon model selection, which might 
take some minutes while the 3D Slicer interface won't be responding.  

The main Docker image can also be downloaded manually:
```
docker pull dbouget/raidionics-rads:v1.1
```

• When you execute for the first time, you might get a pop-up from Docker asking to allow
the sharing of a .raidonics-slicer directory, accept!

</details>