# virtualflask
A Python/Flask/BASH-based web interface for Oracle VM VirtualBox for Linux systems.

## Setting up virtualflask
### These will get the interface usable
    sudo apt-get update -y
    sudo apt-get install git -y
    sudo git clone https://github.com/skatt621/virtualflask.git
    sudo chown -R ubuntu:ubuntu /home/ubuntu/virtualflask
    cd virtualflask
    ./installer.sh {IP Address} 8080 21000 29000
**REMINDER:** Place some iso files in the ISOS folder  

## Initial Instructions
### These will create a usable template VM for the copy function to work
### **NOTE: THE COPY FUNCTION CURRENTLY ONLY WORKS FOR APT-BASED OPERATING SYSTEMS**
1. Change to the WEBAPP directory and run flaskapp.py like this:  

        cd /home/ubuntu/virtualflask/WEBAPP
        python3 flaskapp.py

2. Use the web interface to "Create New VM from ISO". Use an Ubuntu 16 Desktop iso and use the name "ubuntu_16_d_base".
3. Login to the new VM over RDP.
4. Run the following steps:  

        sudo apt-get update -y; sudo apt-get upgrade -y
        sudo apt-get install openssh-server network-manager -y
        sudo passwd root #{use password "password"}
        sudo sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/g" /etc/ssh/sshd_config
        sudo sed -i "s/PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config
        sudo service ssh restart
        cat /dev/null > ~/.bash_history && history -c && exit

5. Turn off the VM from the host by running this:

        vboxmanage controlvm ubuntu_16_d_base poweroff

6. Copy the VM files to the BASE directory like this:  

        cp -R /home/ubuntu/virtualflask/VMS/ubuntu_16_d_base /home/ubuntu/virtualflask/BASE/ubuntu_16_d_base

7. Use the delete VM script to delete the VM from the VMS directory.

        /home/ubuntu/virtualflask/VMEXE/dvm.sh ubuntu_16_d_base

**ALTERNATIVELY** Download the tar archive "bases.tar.gz" (https://drive.google.com/file/d/1G3HNr7kADHn40RFbbetx2ml-lOaYGvLk/view?usp=sharing), place in the BASE directory, and extract. Then remove the tar archive.
