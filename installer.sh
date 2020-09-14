#!/bin/bash
# $1 = IP address, $2 = web port, $3 = port range lower bound, $4 = port range upper bound
set -e
set -x

sudo apt-get update -y
sudo apt-get install python3-pip -y
sudo pip3 install flask
sudo pip3 install django

sudo apt-get install virtualbox -y
sudo curl https://download.virtualbox.org/virtualbox/5.2.44/Oracle_VM_VirtualBox_Extension_Pack-5.2.44.vbox-extpack > Oracle_VM_VirtualBox_Extension_Pack-5.2.44.vbox-extpack
sudo vboxmanage extpack install Oracle_VM_VirtualBox_Extension_Pack-5.2.44.vbox-extpack

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

#cd $(pwd)/BASE
#tar -xzvf ubuntu_16_d_base
#rm ubuntu_16_d_base.tar.gz
#tar -xzvf ubuntu_16_s_base
#rm ubuntu_16_s_base.tar.gz
#cd -
