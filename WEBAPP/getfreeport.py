import os
import random
import socket

PORT_RANGE = {{{RANGE}}}
def getfreeport():
    usedports = []
    vm_list = os.listdir("{{{DIREC}}}/VMS") 

    for i in vm_list:
        f = open("{{{DIREC}}}/VMS/{0}/details.txt".format(i), 'r')
        contents = f.read().strip()
        f.close()
        contents = contents.split("\n")
        usedports.append(contents[5])

    port = 0
    found = False
    while not found:
        num = random.randint(PORT_RANGE[0], PORT_RANGE[-1])
        avail = False
        s = socket.socket()
        try:
            s.bind(("", num))
            s.close()
            avail = True
        except OSError:
            avail =  False

        if (num not in usedports) and avail:
            found = True
            port = num

    return port

print(str(getfreeport()))
