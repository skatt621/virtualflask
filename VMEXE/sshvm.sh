#!/bin/bash
# $1 = VM name, $2 = username, $3 = password
set -x

echo "PROVISIONING STEPS"
echo "$1"
echo "$2"
echo "$3"

elporto=`python getfreeport.py`

echo "############1"
ssh-keygen -f /home/$USER/.ssh/known_hosts -R [127.0.0.1]:$elporto
echo "############2"
VBoxManage controlvm "$1" poweroff
echo "############3"
VBoxManage modifyvm "$1" --natpf1 "hostssh,tcp,,$elporto,,22"
echo "############4"
VBoxManage startvm "$1" --type headless
echo "############5"
echo password > ./pass

ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o PubkeyAuthentication=no -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no -o ChallengeResponseAuthentication=no -p $elporto 127.0.0.1 2>&1 | fgrep -q "Permission denied"
while test $? -gt 0
do
    echo "try"
    sleep 10
    ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o PubkeyAuthentication=no -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no -o ChallengeResponseAuthentication=no -p $elporto 127.0.0.1 2>&1 | fgrep -q "Permission denied"
done
echo "done trying"

sshpass -f ./pass ssh -p $elporto "root@127.0.0.1" -oStrictHostKeyChecking=no "bash -s" < {{{DIREC}}}/VMEXE/userpasshostssh.sh "$1" "$2" "$3"

rm pass
echo "############6"
VBoxManage controlvm "$1" poweroff

echo "############7"
VBoxManage modifyvm "$1" --natpf1 delete "hostssh"

echo "############8"
VBoxManage startvm "$1" --type headless

echo "############9"
rm "{{{DIREC}}}/WEBAPP/error_$1.log"
