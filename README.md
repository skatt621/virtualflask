# VirtualBox_IaC
Python/BASH-based web interface for Oracle VM VirtualBox.

## Setting up VirtualBox_IaC
1. sudo apt-get update -y
2. sudo apt-get install git -y
3. sudo git clone https://github.com/skatt621/VirtualBox_IaC.git
4. sudo chown -R ubuntu:ubuntu /home/ubuntu/VirtualBox_IaC
5. cd VirtualBox_IaC
6. ./installer.sh /home/ubuntu/VirtualBox_IaC {IP Address} 8080 21000 29000
7. **REMINDER:** Place some iso files in the ISOS folder and edit the dictionaries at the top of flaskapp.py accordingly.

## Initial Instructions
1. Change to the WEBAPP directory and run flaskapp.py like this:  
    cd /home/ubuntu/VirtualBox_IaC/WEBAPP  
    python3 flaskapp.py  

2. Use the web interface to "Create New VM from ISO". Use the Ubuntu 16.04.07 Desktop ISO and use the name "ubuntu_16_d_base".
3. Login to the new VM over RDP.
4. Change the username to "msudo".
5. Change the password to "pass".
6. Install OpenSSH server and enable/start it.
7. Allow password log in as well as root SSH.
8. Power off the VM from the commandline like this:  
    sudo shutdown 0  

9. Copy the VM files to the BASE directory like this:  
    cp -R ../VMS/Ubuntu_16_D_BASE ../BASE/Ubuntu_16_D_BASE  

10. Use the delete VM script to delete the VM from the VMS directory.  
    ../VMEXE/dvm.sh Ubuntu_16_D_BASE

11.  **ALTERNATIVELY** Download the tar archive "bases.tar.gz" (https://drive.google.com/file/d/1Eaw3GUt8RbxaOOaKxyqe5eeH9lF3rSCh/view?usp=sharing), place in the BASES directory, and extract.
