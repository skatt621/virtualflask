#!/bin/bash
# $1 = name, $2 = base, $3 = port, $4 = uuid, $5 = username, $6 = password, $7 = mode, $8 = mem
set -x

# ==============================================
# ==============================================

VBoxManage createvm --basefolder "{{{DIREC}}}/VMS" --name $1 --uuid=$4 --ostype $2 --register
VBoxManage modifyvm $1 --cpus 1 --memory $8 --vram 12
echo "================="
echo "VM CREATED"

touch {{{DIREC}}}/VMS/$1/details.txt
echo "====DETAILS====" > {{{DIREC}}}/VMS/$1/details.txt
echo "STATE: PROVISIONING" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VM name: $1" >> {{{DIREC}}}/VMS/$1/details.txt
echo "OS type: $2" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VM base type: $2" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VRDE port: $3" >> {{{DIREC}}}/VMS/$1/details.txt
echo "UUID: $4" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Username: $5" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Password: $6" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Connection mode: $7" >> {{{DIREC}}}/VMS/$1/details.txt
echo "================="
echo "DETAILS RECORDED"

VBoxManage clonevdi "{{{DIREC}}}/BASE/$2/$2.vdi" "{{{DIREC}}}/VMS/$1/$1.vdi"
VBoxManage storagectl $1 --name "SATA Controller" --add sata --bootable on
VBoxManage storageattach $1 --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "{{{DIREC}}}/VMS/$1/$1.vdi"
echo "================="
echo "VDI CLONED AND ATTACHED"

if [ "$7" == "RDP" ]
then
    VBoxManage modifyvm $1 --vrde on --vrdeport $3 --vrdeaddress {{{ADDRESS}}}
    echo "================="
    echo "VRDE TURNED ON"
fi

if [ "$7" == "SSH" ]
then
    VBoxManage modifyvm "$1" --natpf1 "hostssh,tcp,,$port,,22"
    echo "================="
    echo "SSH TURNED ON"
fi

VBoxManage startvm $1 --type headless

if [ $2 = "Ubuntu_64" ]
then
    {{{DIREC}}}/VMEXE/sshvm.sh $1 $5 $6
    sed -i "s/STATE: PROVISIONING/STATE: RUNNING/g" {{{DIREC}}}/VMS/$1/details.txt
fi

if [ $2 = "Windows10_64" ]
then
    # Not implemented
    {{{DIREC}}}/VMEXE/sshvm-win.sh $1 $5 $6
fi
echo "================="
echo "VM PROVISIONED AND DETAILS ADDED"
