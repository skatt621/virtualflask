#!/bin/bash
# $1 = old IP, $2 = new IP
set -e
set -x

declare -a file_list=( "./WEBAPP/flaskapp.py" "./WEBAPP/getfreeport.py" "./VMEXE/cvm.sh" "./VMEXE/cpvm.sh" "./VMEXE/sshvm.sh" "./VMEXE/dvm.sh" )

for i in "${file_list[@]}"
do 
    sed -i "s|$1|$2|g" $i
done
