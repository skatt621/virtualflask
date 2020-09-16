#!/bin/bash
set -x

for var in "$@"
do
    VBoxManage controlvm $var poweroff
    VBoxManage unregistervm $var
    rm -r "{{{DIREC}}}/VMS/$var"
    rm -r "{{{DIREC}}}/WEBAPP/static/$var"
    rm "{{{DIREC}}}/WEBAPP/error_$var.log"
done
