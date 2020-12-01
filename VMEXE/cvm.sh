#!/bin/bash
# $1=name, $2=isopath, $3=port, $4=uuid, $5=mode, $6=hddrive in megabytes, $7=memory in megabytes
set -x

# ==============================================
# ==============================================

VBoxManage createvm --basefolder "{{{DIREC}}}/VMS" --name $1 --uuid=$4 --register
VBoxManage modifyvm $1 --cpus 1 --memory $7 --vram 16
VBoxManage modifyvm $1 --acpi on --ioapic on --pae off --x2apic on --rtcuseutc on
echo "================="
echo "VM CREATED"

touch {{{DIREC}}}/VMS/$1/details.txt
echo "====DETAILS====" > {{{DIREC}}}/VMS/$1/details.txt
echo "STATE: PROVISIONING" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VM name: $1" >> {{{DIREC}}}/VMS/$1/details.txt
echo "ISO file: $2" >> {{{DIREC}}}/VMS/$1/details.txt
echo "VRDE port: $3" >> {{{DIREC}}}/VMS/$1/details.txt
echo "UUID: $4" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Connection mode: $5" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Hard drive size (in MB): $6" >> {{{DIREC}}}/VMS/$1/details.txt
echo "Memory size (in MB): $7" >> {{{DIREC}}}/VMS/$1/details.txt
echo "================="
echo "DETAILS RECORDED"

VBoxManage createhd --filename "{{{DIREC}}}/VMS/$1/$1.vdi" --size $6 --variant Standard
VBoxManage storagectl $1 --name "SATA Controller" --add sata --bootable on
VBoxManage storageattach $1 --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "{{{DIREC}}}/VMS/$1/$1.vdi"
echo "================="
echo "VDI CREATED AND ATTACHED"

VBoxManage storagectl $1 --name "IDE Controller" --add ide
VBoxManage storageattach $1 --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "{{{DIREC}}}/ISOS/$2"
echo "================="
echo "IDE CONTROLLER CREATED AND ISO ATTACHED"

VBoxManage modifyvm $1 --vrde on --vrdeport $3
echo "================="
echo "VRDE TURNED ON"

if [ "$5" == "RDP" ]
then
    VBoxManage modifyvm $1 --vrde on --vrdeport $3 --vrdeaddress {{{ADDRESS}}}
    echo "================="
    echo "VRDE TURNED ON"
fi

if [ "$5" == "SSH" ]
then
    VBoxManage modifyvm "$1" --natpf1 "hostssh,tcp,,$3,,22"
    echo "================="
    echo "SSH TURNED ON"
fi

vboxmanage modifyvm "$1" --nic1 NAT
VBoxManage startvm $4 --type headless
echo "================="
echo "VM STARTED"

cat {{{DIREC}}}/VMS/$1/details.txt | sed "s/STATE: PROVISIONING/STATE: RUNNING/g" > {{{DIREC}}}/VMS/$1/details2.txt
cat {{{DIREC}}}/VMS/$1/details2.txt > {{{DIREC}}}/VMS/$1/details.txt
rm {{{DIREC}}}/VMS/$1/details2.txt
echo "================="
echo "DETAILS ADDED"

rm "{{{DIREC}}}/WEBAPP/error_$1.log"
