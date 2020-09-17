#!/bin/bash
# $1 = name, $2 = type, $3 = base, $4 = port, $5 = uuid, $6 = username, $7 = password, $8 = mode, $9 = mem
set -x

# ==============================================
# ==============================================

VBoxManage createvm --basefolder "{{{DIREC}}}/VMS" --name $1 --uuid=$5 --ostype $2 --register
VBoxManage modifyvm $1 --cpus 1 --memory $9 --vram 12
echo "================="
echo "VM CREATED"

touch {{{DIREC}}}/VMS/$1/details.txt
echo "====DETAILS====" > {{{DIREC}}}/VMS/$1/details.txt
echo "STATE: PROVISIONING" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VM name: $1" >> {{{DIREC}}}/VMS/$1/details.txt
echo "OS type: $2" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VM base type: $3" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VRDE port: $4" >> {{{DIREC}}}/VMS/$1/details.txt
echo "UUID: $5" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Username: $6" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Password: $7" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Connection mode: $8" >> {{{DIREC}}}/VMS/$1/details.txt
echo "================="
echo "DETAILS RECORDED"

VBoxManage clonevdi "{{{DIREC}}}/BASE/$3/$3.vdi" "{{{DIREC}}}/VMS/$1/$1.vdi"
VBoxManage storagectl $1 --name "SATA Controller" --add sata --bootable on
VBoxManage storageattach $1 --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "{{{DIREC}}}/VMS/$1/$1.vdi"
echo "================="
echo "VDI CLONED AND ATTACHED"

if [ "$8" == "RDP" ]
then
    VBoxManage modifyvm $1 --vrde on --vrdeport $4 --vrdeaddress {{{ADDRESS}}}
    echo "================="
    echo "VRDE TURNED ON"
fi

if [ "$8" == "SSH" ]
then
    VBoxManage modifyvm "$1" --natpf1 "hostssh,tcp,,$port,,22"
    echo "================="
    echo "SSH TURNED ON"
fi

VBoxManage startvm $1 --type headless

if [ $2 = "Ubuntu_64" ]
then
    {{{DIREC}}}/VMEXE/sshvm.sh $1 $6 $7
    sed -i "s/STATE: PROVISIONING/STATE: RUNNING/g" {{{DIREC}}}/VMS/$1/details.txt
fi

if [ $2 = "Windows10_64" ]
then
    # Not implemented
    {{{DIREC}}}/VMEXE/sshvm-win.sh $1 $6 $7
fi
echo "================="
echo "VM PROVISIONED AND DETAILS ADDED"
