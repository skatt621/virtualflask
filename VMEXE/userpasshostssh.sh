#!/bin/bash                                                                                                                                              
# $1=new host name, $2=new user name, $3=password                                
set -x                                                                           
                                                                                 
echo "msudo:$3" | chpasswd                                                       
usermod -l "$2" msudo                                                            
chfn -f "$2" "$2"                                                                
usermod -d "/home/$2" -m "$2"                                                    
                                                                                 
sed -i 's/^PermitRootLogin yes/PermitRootLogin prohibit-password/g' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/#PasswordAuthentication yes/g' /etc/ssh/sshd_config
service ssh restart                                                              
                                                                                 
sudo apt-get install network-manager -y
sudo nmcli networking off                                                        
sudo hostnamectl set-hostname $1                                                 
sed -i "s/msudo/$1/g" /etc/hosts                                                 
echo "$1" > /etc/hostname                                                        
cat /etc/hosts                                                                   
cat /etc/hostname                                                                
sudo nmcli networking on                                                         
sudo hostnamectl
