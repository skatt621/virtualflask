#!/bin/bash
# $1 = name, $2 = type, $3 = isopath, $4 = port, $5 = uuid, $6 = username, $7 = password, $8 = mode

# ==============================================
# ==============================================
# CAUTION: NOT WORKING, DO NOT USE

VBoxManage createvm --basefolder "/home/clouduser/VirtualBox_IaC/VMS" --name $1 --uuid=$5 --ostype $2 --register
VBoxManage modifyvm $1 --cpus 1 --memory 512 --vram 12
echo "================="
echo "VM CREATED"

mkdir /home/clouduser/VirtualBox_IaC/VMS/$1
touch /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "====DETAILS====" > /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "STATE: PROVISIONING" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "$1" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "$2" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "$3" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "$4" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "$5" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "$6" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "$7" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "$8" >> /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
echo "================="
echo "DETAILS RECORDED"

VBoxManage createhd --filename "/home/clouduser/VirtualBox_IaC/VMS//$1/$1.vdi" --size 10000 --variant Standard
VBoxManage storagectl $1 --name "SATA Controller" --add sata --bootable on
VBoxManage storageattach $1 --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "/home/clouduser/VirtualBox_IaC/VMS/$1/$1.vdi"
echo "================="
echo "VDI CREATED AND ATTACHED"

VBoxManage storagectl $1 --name "IDE Controller" --add ide
#VBoxManage storageattach $1 --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "/home/clouduser/VirtualBox_IaC/ISOS/$3"
echo "================="
echo "IDE CONTROLLER CREATED AND ISO ATTACHED"

if [ "$8" == "RDP" ]
then
    VBoxManage modifyvm $1 --vrde on --vrdeport $4
    echo "================="
    echo "VRDE TURNED ON"

    VBoxManage unattended install $1 --iso=/home/clouduser/VirtualBox_IaC/ISOS/$3 --user=$6 --full-user-name=$6 --password=$7 --script-template /usr/share/virtualbox/UnattendedTemplates/ubuntu_preseed.cfg --post-install-template /usr/share/virtualbox/UnattendedTemplates/debian_newpostinstall.sh --post-install-command="sudo systemctl enable ufw; sudo usermod -aG sudo $6"
fi

if [ "$8" == "SSH" ]
then
    let port=$4-1
    VBoxManage modifyvm $1 --vrde on --vrdeport $port
    echo "================="
    echo "VRDE TURNED ON"
    VBoxManage modifyvm "$1" --natpf1 "hostssh,tcp,,$4,,22"
    echo "================="
    echo "SSH TURNED ON"

    if [[ "$3" == "ubuntu"*"16"*".iso" ]]
    then
        VBoxManage unattended install $1 --iso=/home/clouduser/VirtualBox_IaC/ISOS/$3 --user=$6 --full-user-name=$6 --password=$7 --time-zone=CET --script-template /usr/share/virtualbox/UnattendedTemplates/ubuntu_preseed.cfg --post-install-template /usr/share/virtualbox/UnattendedTemplates/debian_postinstall.sh
    fi
    if [[ "$3" == "ubuntu"*"18"*".iso" ]]
    then
        VBoxManage unattended install $1 --iso=/home/clouduser/VirtualBox_IaC/ISOS/$3 --user=$6 --full-user-name=$6 --password=$7 --time-zone=CET
    fi
    if [[ "$3" == "ubuntu"*"20"*".iso" ]]
    then
        VBoxManage unattended install $1 --iso=/home/clouduser/VirtualBox_IaC/ISOS/$3 --user=$6 --full-user-name=$6 --password=$7 --time-zone=CET
    fi
    
fi

VBoxManage startvm $5 --type headless
echo "================="
echo "UNATTENDED INSTALL STARTED"

cat /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt | sed "s/STATE: PROVISIONING/STATE: RUNNING/g" > /home/clouduser/VirtualBox_IaC/VMS/$1/details2.txt
cat /home/clouduser/VirtualBox_IaC/VMS/$1/details2.txt > /home/clouduser/VirtualBox_IaC/VMS/$1/details.txt
rm /home/clouduser/VirtualBox_IaC/VMS/$1/details2.txt
echo "================="
echo "DETAILS ADDED"
