#!/bin/bash
# $1 = IP address, $2 = web port, $3 = port range lower bound, $4 = port range upper bound

sudo apt-get update -y
sudo apt-get install python3-pip curl -y
sudo pip3 install flask
sudo pip3 install django

sudo apt-get install virtualbox -y
vboxver=`vboxmanage --version | awk -F '_' '{print $1}'
sudo curl https://download.virtualbox.org/virtualbox/$vboxver/Oracle_VM_VirtualBox_Extension_Pack-$vboxver.vbox-extpack > Oracle_VM_VirtualBox_Extension_Pack-$vboxver.vbox-extpack
echo "y" | sudo vboxmanage extpack install Oracle_VM_VirtualBox_Extension_Pack-$vboxver.vbox-extpack
sudo vboxmanage extpack uninstall --force VNC

declare -a file_list=( "./WEBAPP/flaskapp.py" "./WEBAPP/getfreeport.py" "./VMEXE/cvm.sh" "./VMEXE/cpvm.sh" "./VMEXE/sshvm.sh" "./VMEXE/dvm.sh" )

for i in "${file_list[@]}"
do 
    sed -i "s|{{{DIREC}}}|$(pwd)|g" $i
    sed -i "s|{{{ADDRESS}}}|$1|g" $i
    sed -i "s|{{{PORT}}}|$2|g" $i
    sed -i "s|{{{RANGE}}}|range($3, $4)|g" $i
done

rm "$(pwd)/BASE/.placeholder"
rm "$(pwd)/ISOS/.placeholder"
rm "$(pwd)/VMS/.placeholder"
rm "$(pwd)/WEBAPP/.placeholder"
rm "$(pwd)/WEBAPP/static/.placeholder"
rm "$(pwd)/VMEXE/.placeholder"
rm -rf "$(pwd)/.git"
