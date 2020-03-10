Installation

• Download 3DSlicer.  
• Install DeepSintef Module:  
∘ Download locally the module from github.  
∘ All Modules > Extension Wizard.  
∘ Select Extension > point to the folder and add it to the path (tick the small box at the bottom).  
• Install docker:  
∘ Ubuntu: https://docs.docker.com/install/linux/docker-ce/ubuntu/  
‣ sudo apt-get update  
‣ sudo apt-get install \ 
		    apt-transport-https \   
		    ca-certificates \ 
		    curl \ 
		    gnupg-agent \   
		    software-properties-common   
‣ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - 
‣ sudo apt-key fingerprint 0EBFCD88   
‣ sudo apt-get install docker-ce docker-ce-cli containerd.io  
• Login into your docker account (e.g., 'docker login' on ubuntu)  
• Put the *.json file inside the ~/.deepsintef/json/local folder  
• Download the docker image (have to be logged in to work).  