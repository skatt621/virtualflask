#!/bin/bash
# $1 = name, $2 = type, $3 = isopath, $4 = port, $5 = uuid $6 = mode
set -x

# ==============================================
# ==============================================

VBoxManage createvm --basefolder "{{{DIREC}}}/VMS" --name $1 --uuid=$5 --ostype $2 --register
VBoxManage modifyvm $1 --cpus 1 --memory 1024 --vram 12
echo "================="
echo "VM CREATED"

touch {{{DIREC}}}/VMS/$1/details.txt
echo "====DETAILS====" > {{{DIREC}}}/VMS/$1/details.txt
echo "STATE: PROVISIONING" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VM name: $1" >> {{{DIREC}}}/VMS/$1/details.txt
echo "OS type: $2" >> {{{DIREC}}}/VMS/$1/details.txt
echo "ISO file: $3" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VRDE port: $4" >> {{{DIREC}}}/VMS/$1/details.txt
echo "UUID: $5" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Connection mode: $6" >> {{{DIREC}}}/VMS/$1/details.txt
echo "================="
echo "DETAILS RECORDED"

VBoxManage createhd --filename "{{{DIREC}}}/VMS/$1/$1.vdi" --size 10000 --variant Standard
VBoxManage storagectl $1 --name "SATA Controller" --add sata --bootable on
VBoxManage storageattach $1 --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "{{{DIREC}}}/VMS/$1/$1.vdi"
echo "================="
echo "VDI CREATED AND ATTACHED"

VBoxManage storagectl $1 --name "IDE Controller" --add ide
VBoxManage storageattach $1 --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "{{{DIREC}}}/ISOS/$3"
echo "================="
echo "IDE CONTROLLER CREATED AND ISO ATTACHED"

VBoxManage modifyvm $1 --vrde on --vrdeport $4
echo "================="
echo "VRDE TURNED ON"

if [ "$6" == "RDP" ]
then
    VBoxManage modifyvm $1 --vrde on --vrdeport $4 --vrdeaddress {{{ADDRESS}}}
    echo "================="
    echo "VRDE TURNED ON"
fi

if [ "$6" == "SSH" ]
then
    VBoxManage modifyvm "$1" --natpf1 "hostssh,tcp,,$4,,22"
    echo "================="
    echo "SSH TURNED ON"
fi

VBoxManage startvm $5 --type headless
echo "================="
echo "VM STARTED"

cat {{{DIREC}}}/VMS/$1/details.txt | sed "s/STATE: PROVISIONING/STATE: RUNNING/g" > {{{DIREC}}}/VMS/$1/details2.txt
cat {{{DIREC}}}/VMS/$1/details2.txt > {{{DIREC}}}/VMS/$1/details.txt
rm {{{DIREC}}}/VMS/$1/details2.txt
echo "================="
echo "DETAILS ADDED"

rm "{{{DIREC}}}/WEBAPP/error_$1.log"
