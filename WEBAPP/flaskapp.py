# Packages used
import sys
import subprocess
from subprocess import Popen, PIPE
import os
import socket
import time
from datetime import datetime
from flask import Flask, redirect, request, session, abort, render_template, make_response, flash, send_from_directory
from functools import wraps, update_wrapper
import uuid
import random
from django.template.defaultfilters import slugify

# Python function imports
from getfreeport import getfreeport

# Flask settings for app name/details, file serving location, and disabling caching of files
app = Flask(__name__, static_url_path="/static")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Dictionaries used to translate HTML form arguments into VM creation/copying arguments
# ! CHANGE THESE BASED ON THE ISOS IN YOUR "ISOS" FOLDER !
# Values for the first can be found bu running 'VBoxManage list ostypes'
type_type_dict = {
"Ubuntu_16_D":"Ubuntu_64", 
"Ubuntu_16_S":"Ubuntu_64", 
"Ubuntu_18_D":"Ubuntu_64", 
"Ubuntu_18_S":"Ubuntu_64", 
"Ubuntu_20_D":"Ubuntu_64", 
"Ubuntu_20_S":"Ubuntu_64"}

type_iso_dict = {
"Ubuntu_16_D":"ubuntu-16.04.7-desktop-amd64.iso", 
"Ubuntu_16_S":"ubuntu-16.04.7-server-amd64.iso", 
"Ubuntu_18_D":"ubuntu-18.04.4-desktop-amd64.iso", 
"Ubuntu_18_S":"ubuntu-18.04.4-live-server-amd64.iso", 
"Ubuntu_20_D":"ubuntu-20.04.1-desktop-amd64.iso", 
"Ubuntu_20_S":"ubuntu-20.04.1-live-server-amd64.iso"}

type_base_dict = {
"Ubuntu_16_D":"Ubuntu_16_D_BASE", 
"Ubuntu_16_S":"Ubuntu_16_S_BASE"}

# Setting a port range for serving RDP/SSH connections
PORT_RANGE = {{{RANGE}}}

# Basic RDP file setup; formatted and saved as a static file then served
RDP = """
screen mode id:i:2
use multimon:i:0
desktopwidth:i:1920
desktopheight:i:1080
session bpp:i:32
winposstr:s:0,1,626,145,1717,1050
compression:i:1
keyboardhook:i:2
audiocapturemode:i:0
videoplaybackmode:i:1
connection type:i:7
networkautodetect:i:1
bandwidthautodetect:i:1
displayconnectionbar:i:1
enableworkspacereconnect:i:0
disable wallpaper:i:0
allow font smoothing:i:0
allow desktop composition:i:0
disable full window drag:i:1
disable menu anims:i:1
disable themes:i:0
disable cursor setting:i:0
bitmapcachepersistenable:i:1
full address:s:{0}
audiomode:i:0
redirectprinters:i:1
redirectcomports:i:0
redirectsmartcards:i:1
redirectclipboard:i:1
redirectposdevices:i:0
autoreconnection enabled:i:1
authentication level:i:2
prompt for credentials:i:0
negotiate security layer:i:1
remoteapplicationmode:i:0
alternate shell:s:
shell working directory:s:
gatewayhostname:s:
gatewayusagemethod:i:4
gatewaycredentialssource:i:4
gatewayprofileusagemethod:i:0
promptcredentialonce:i:0
gatewaybrokeringtype:i:0
use redirection server name:i:0
rdgiskdcproxy:i:0
kdcproxyname:s:
"""

@app.route('/')
def index():
    # Setting "online" argument to "Yes"
    session['online'] = "Yes"

    # Resetting all possible flask session tokens
    session['name'] = ""
    session['mode'] = ""
    session['uuid'] = ""
    session['port'] = ""
    session['username'] = ""
    session['password'] = ""
    session['type'] = ""
    session['date'] = ""
    session['filename'] = ""
    session['error_iso'] = ""
    session['error_base'] = ""

    return redirect('/iso')

@app.route('/iso')
def iso():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/")

    # Generating an access port and a UUID to be used in a new iso-based VM
    assigned_port = str(getfreeport())
    assigned_uuid = str(uuid.uuid1())

    # Using flask session tokens to display any errors
    errors = session['error_iso'].split("INVALID")
    errors.remove("")
    error_msg = ("<br></br>").join(errors)

    # Formatting and returning HTML
    f = open('iso.html', 'r')
    html = f.read()
    f.close()
    html = html.format(assigned_port, assigned_uuid , error_msg)
    return html

@app.route('/base', methods=['GET', 'POST'])
def base():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/")

    # Checking for the various template VMS available
    select_options = ""
    vm_dlist = os.listdir("{{{DIREC}}}/BASE") 
    for i in vm_dlist:
        select_options += "<option value=\"{0}\">{0}</option>".format(i)

    # Generating an access port and a UUID to be used in a new template-based VM
    assigned_port = str(getfreeport())
    assigned_uuid = str(uuid.uuid1())

    # Using flask session tokens to display any errors
    errors = session['error_base'].split("INVALID")
    errors.remove("")
    error_msg = ("<br></br>").join(errors)

    # Formatting and returning HTML
    f = open('base.html', 'r')
    html = f.read()
    f.close()
    html = html.format(assigned_port, assigned_uuid, error_msg, select_options)
    return html

@app.route('/create', methods=['GET', 'POST'])
def create():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/")

    session['error_iso'] = ""
    vm_dlist = os.listdir("{{{DIREC}}}/VMS") 
    if slugify(request.args.get('NAME')) in vm_dlist:
        session['error_iso'] += "INVALID NAME {0} : ALREADY TAKEN".format(request.args.get('NAME'))

    if session['error_iso'] != "":
        return redirect("/iso")

    # Arguments to be used by the VM creation script
    ipadd = "{{{ADDRESS}}}"
    name = slugify(request.args.get('NAME'))
    mode = request.args.get('MODE')
    type = type_type_dict[request.args.get('TYPE')]
    iso = type_iso_dict[request.args.get('TYPE')]
    port = request.args.get('PORT')
    uuid = request.args.get('UUID')

    # Setting various session tokens to be used by the "down" function; displayed to user
    session['name'] = name
    session['type'] = type
    session['port'] = port
    session['uuid'] = uuid
    
    # Opening a process to create a VM and waiting to continue before the "details" file is created
    subprocess.Popen("{{{DIREC}}}/VMEXE/cvm.sh \"{0}\" \"{1}\" \"{2}\" \"{3}\" \"{4}\" \"{5}\">> error_{6}.log 2>&1".format(name, type, iso, port, uuid, mode, name), shell = True, stdout=subprocess.PIPE)

    # Creating a directory in the "static" folder and placing an RDP file there to be served
    filename = "/static/{0}/{0}.rdp".format(name)
    filename = filename.format(name)

    os.mkdir("static/{0}".format(name))
    newrdp = RDP.format(ipadd + ":" + port)
    fo = open(filename[1:], "w")
    fo.write(newrdp)
    fo.close() 

    # Redirection to the download details page
    return redirect("/down")

@app.route('/copy', methods=['GET', 'POST'])
def copy():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/")

    session['error_base'] = ""

    vm_dlist = os.listdir("{{{DIREC}}}/VMS") 
    if slugify(request.args.get('NAME')) in vm_dlist:
        session['error_base'] += "INVALID NAME {0} : ALREADY TAKEN".format(request.args.get('NAME'))

    if session['error_base'] != "":
        return redirect("/base")

    # Arguments to be used by the VM creation script
    ipadd = "{{{ADDRESS}}}"
    name = slugify(request.args.get('NAME'))
    #base = type_base_dict[request.args.get('TYPE')]
    base = request.args.get('TYPE')
    port = request.args.get('PORT')
    uuid = request.args.get('UUID')
    username = slugify(request.args.get('USERNAME'))
    password = slugify(request.args.get('PASSWORD'))

    # Getting information from template VM files for certain script arguments
    #############
    f = open("{{{DIREC}}}/BASE/{0}/details.txt".format(base), 'r')
    contents = f.read().strip()
    f.close()
    contents = contents.split("\n")
    for det in contents:
        try:
            det = det.split(": ")[1]
        except:
            det = det

    type = contents[3]
    mode = contents[7]
    #############

    # Setting various session tokens to be used by the "down" function; displayed to user
    session['name'] = name
    session['type'] = type
    session['port'] = port
    session['uuid'] = uuid
    session['username'] = username
    session['password'] = password
    
    # Opening a process to create a VM and waiting to continue before the "details" file is created
    subprocess.Popen("{{{DIREC}}}/VMEXE/cpvm.sh \"{0}\" \"{1}\" \"{2}\" \"{3}\" \"{4}\" \"{5}\" \"{6}\" \"{7}\" >> error_{8}.log 2>&1".format(name, type, base, port, uuid, username, password, mode, name), shell = True, stdout=subprocess.PIPE)

    while not (os.path.isfile("{{{DIREC}}}/VMS/{0}/details.txt".format(name))):
        time.sleep(1) 

    # Creating a directory in the "static" folder and placing an RDP file there to be served
    filename = "/static/{0}/{0}.rdp".format(name)
    filename = filename.format(name)

    os.mkdir("static/{0}".format(name))
    newrdp = RDP.format(ipadd + ":" + port)
    fo = open(filename[1:], "w")
    fo.write(newrdp)
    fo.close() 

    # Redirection to the download details page
    return redirect("/down")

@app.route('/down', methods=['GET', 'POST'])
def down():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/") 

    # Formatting and returning HTML using session tokens
    f = open('down.html', 'r')
    html = f.read()
    f.close()
    return html.format(session['name'], session['type'], session['port'], session['uuid'], session['username'], session['password']) 

@app.route('/select', methods=['GET', 'POST'])
def select():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/")
    
    # Resetting session tokens so moving to other pages from the select page doesn't crash 
    session['name'] = ""
    session['uuid'] = ""
    session['port'] = ""
    session['username'] = ""
    session['password'] = ""
    session['type'] = ""
    session['date'] = ""
    session['filename'] = ""

    # Getting a list of available VMs
    list_html = ""
    vm_dlist = os.listdir("{{{DIREC}}}/VMS") 

    # For every VM available, checking the "State" in each details file to evaluate if it is running before presenting an RDP download/SSH connection option
    for i in vm_dlist:
    #############
        f = open("{{{DIREC}}}/VMS/{0}/details.txt".format(i), 'r')
        contents = f.read().strip()
        f.close()
        contents = contents.split("\n")

        for det in contents:
            try:
                det = det.split(": ")[1]
            except:
                det = det
    #############

        state=(contents[1].split(": ")[1]).strip()
        running = False

        p = subprocess.run("vboxmanage list runningvms | awk -F ' ' '{ print $1 }' | sed 's/\"//g' > file; cat file | tr '\n' '|' | sed 's/\(.*\)|/\\1 /'; rm file", shell = True, stdout=subprocess.PIPE)
        runlist = p.stdout.decode("utf-8").split("|")
        for j in range(0, len(runlist)):
            runlist[j] = runlist[j].strip()

        if i in runlist:
            running = True

        if state == "RUNNING":
            if running:
                list_html += """
                             <h3> <a href={0}>{1}</a> </h3>
                             <form action="/edit">
                                 <input type='hidden' name='NAME' value='{1}'/>
                                 <button type='submit' name='ACTION' value='poweron' disabled>Power on</button>
                                 <button type='submit' name='ACTION' value='poweroff'>Power off</button>
                                 <button type='submit' name='ACTION' value='delete'>DELETE</button>
                             </form>
                             <br> </br>""".format("static/" + i + "/" + os.listdir("static/" + i)[0], i)
            else:
                list_html += """
                             <h3> <a href={0}>{1}</a> </h3>
                             <form action="/edit">
                                 <input type='hidden' name='NAME' value='{1}'/>
                                 <button type='submit' name='ACTION' value='poweron'>Power on</button>
                                 <button type='submit' name='ACTION' value='poweroff' disabled>Power off</button>
                                 <button type='submit' name='ACTION' value='delete'>DELETE</button>
                             </form>
                             <br> </br>""".format("static/" + i + "/" + os.listdir("static/" + i)[0], i)
        else:
            list_html += """
                         <h3>{0}</h3>
                         <br></br>""".format(i + " (CURRENTLY PROVISIONING)")

    # Formatting and returning HTML
    f = open('select.html', 'r')
    html = f.read()
    f.close()
    return html.format(list_html)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/")
    
    action = request.args.get('ACTION')
    name = request.args.get('NAME')

    if action == "delete":
        subprocess.run("{{{DIREC}}}/VMEXE/dvm.sh \"{0}\" >> error_{0}.log 2>&1".format(name), shell = True, stdout=subprocess.PIPE)

    if action == "poweron":
        subprocess.run("vboxmanage startvm \"{0}\" --type headless >> error_{0}.log 2>&1".format(name), shell = True, stdout=subprocess.PIPE)

    if action == "poweroff":
        subprocess.run("vboxmanage controlvm \"{0}\" poweroff >> error_{0}.log 2>&1".format(name), shell = True, stdout=subprocess.PIPE)

    return redirect("/select")
 
if __name__ == "__main__":
    # Making a session key for each user to set session tokens correctly
    app.secret_key = os.urandom(12)

    # Setting the IP address and port for the flask server to run on
    app.run(host='{{{ADDRESS}}}', port={{{PORT}}})
