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
    session['hdrive'] = ""
    session['mem'] = ""
    session['conn'] = ""

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

    # Adding iso files from the ISOS directory
    iso_html = ""
    iso_dlist = os.listdir("{{{DIREC}}}/ISOS")
    iso_dlist.sort()
    for i in iso_dlist:
        iso_html += "<option value='{0}'>{0}</option>\n".format(i)

    # Formatting and returning HTML
    f = open('iso.html', 'r')
    html = f.read()
    f.close()
    html = html.format(assigned_port, assigned_uuid , error_msg, iso_html)
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

    # Checking for various argument errors for iso-based creation
    session['error_iso'] = ""
    vm_dlist = os.listdir("{{{DIREC}}}/VMS") 

    if slugify(request.args.get('NAME')) in vm_dlist:
        session['error_iso'] += "INVALID NAME {0} : ALREADY TAKEN".format(request.args.get('NAME'))

    if int(request.args.get('HDRIVE')) < 10000:
        session['error_iso'] += "INVALID HARD DRIVE SIZE {0} MB : SIZE LESS THAN 10000 MB (10 GB) NOT ADVISED.".format(request.args.get('HDRIVE'))

    if int(request.args.get('MEM')) < 512:
        session['error_iso'] += "INVALID MEMORY SIZE {0} MB : SIZE LESS THAN 512 MB (0.5 GB) NOT ADVISED.".format(request.args.get('MEM'))

    if session['error_iso'] != "":
        return redirect("/iso")

    # Arguments to be used by the VM creation script
    ipadd = "{{{ADDRESS}}}"
    name = slugify(request.args.get('NAME'))
    mode = request.args.get('MODE')
    iso = request.args.get('ISO')
    port = request.args.get('PORT')
    uuid = request.args.get('UUID')
    hdrive = request.args.get('HDRIVE')
    mem = request.args.get('MEM')

    # Setting various session tokens to be used by the "down" function; displayed to user
    session['name'] = name
    session['type'] = iso
    session['hdrive'] = hdrive
    session['mem'] = mem
    session['port'] = port
    session['conn'] = "RDP"
    session['username'] = ""
    session['password'] = ""
    
    # Opening a process to create a VM and waiting to continue before the "details" file is created
    subprocess.Popen("{{{DIREC}}}/VMEXE/cvm.sh \"{0}\" \"{1}\" \"{2}\" \"{3}\" \"{4}\" \"{5}\" \"{6}\" >> error_{0}.log 2>&1".format(name, iso, port, uuid, mode, hdrive, mem), shell = True, stdout=subprocess.PIPE)

    # Sleep loop until basic VM files are created
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

@app.route('/copy', methods=['GET', 'POST'])
def copy():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/")

    # Checking for various argument errors for iso-based creation
    session['error_base'] = ""
    vm_dlist = os.listdir("{{{DIREC}}}/VMS") 

    if slugify(request.args.get('NAME')) in vm_dlist:
        session['error_base'] += "INVALID NAME {0} : ALREADY TAKEN".format(request.args.get('NAME'))

    if int(request.args.get('MEM')) < 512:
        session['error_base'] += "INVALID MEMORY SIZE {0} MB : SIZE LESS THAN 512 MB (0.5 GB) NOT ADVISED.".format(request.args.get('MEM'))

    if session['error_base'] != "":
        return redirect("/base")

    # Arguments to be used by the VM creation script
    ipadd = "{{{ADDRESS}}}"
    name = slugify(request.args.get('NAME'))
    base = request.args.get('BASE')
    port = request.args.get('PORT')
    uuid = request.args.get('UUID')
    username = slugify(request.args.get('USERNAME'))
    password = slugify(request.args.get('PASSWORD'))
    mem = request.args.get('MEM')

    # Getting information from template VM files for certain script arguments
    f = open("{{{DIREC}}}/BASE/{0}/details.txt".format(base), 'r')
    contents = f.read().strip()
    f.close()
    contents = contents.split("\n")
    for j in range(0, len(contents)): 
        try: 
            contents[j] = contents[j].split(": ")[1] 
        except: 
            contents[j] = contents[j]

    hdrive = contents[7]
    mode = contents[6]

    # Setting various session tokens to be used by the "down" function; displayed to user
    session['name'] = name
    session['type'] = base
    session['hdrive'] = hdrive
    session['mem'] = mem
    session['port'] = port
    session['conn'] = mode
    session['username'] = username
    session['password'] = password
    
    # Opening a process to create a VM and waiting to continue before the "details" file is created
    subprocess.Popen("{{{DIREC}}}/VMEXE/cpvm.sh \"{0}\" \"{1}\" \"{2}\" \"{3}\" \"{4}\" \"{5}\" \"{6}\" \"{7}\" > error_{0}.log 2>&1".format(name, base, port, uuid, username, password, mode, mem), shell = True, stdout=subprocess.PIPE)

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

    # Using flask session tokens to show VM details
    details_html = ""
    details_html += "<li>Name: <strong>{0}</strong></li>\n".format(session['name'])
    details_html += "<li>Type: <strong>{0}</strong></li>\n".format(session['type'])
    details_html += "<li>Hard drive: <strong>{0} MB</strong></li>\n".format(session['hdrive'])
    details_html += "<li>Memory: <strong>{0} MB</strong></li>\n".format(session['mem'])
    details_html += "<li>Port: <strong>{0}</strong></li>\n".format(session['port'])
    details_html += "<li>Connection type: <strong>{0}</strong></li>\n".format(session['conn'])
    
    if session['username'] != "":
        details_html += "<li>Username: <strong>{0}</strong></li>\n".format(session['username'])
        details_html += "<li>Password: <strong>{0}</strong></li>\n".format(session['password'])
    else:
        details_html += "<li><strong>Username and password not set for iso-based creation.</strong></li>\n"

    # Formatting and returning HTML using session tokens
    f = open('down.html', 'r')
    html = f.read()
    f.close()
    return html.format(details_html) 

@app.route('/select', methods=['GET', 'POST'])
def select():
    # Check to force redirection to "/" before any other page is displayed
    if 'online' not in list(session.keys()):
        return redirect("/")
    
    # Resetting session tokens so moving to other pages from the select page doesn't crash 
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
    session['hdrive'] = ""
    session['mem'] = ""
    session['conn'] = ""

    # Getting a list of available VMs
    list_html = ""
    vm_dlist = os.listdir("{{{DIREC}}}/VMS") 

    # For every VM available, checking the "State" in each details file to evaluate which of the three controls (Power on, Power off, and Delete) to show for each.
    # RUNNING VMs display full controls with "Power on" disabled.
    # OFF VMs display full controls with "Power off" disabled.
    # PROVISIONING display only the "Delete" control.
    for i in vm_dlist:
        f = open("{{{DIREC}}}/VMS/{0}/details.txt".format(i), 'r')
        contents = f.read().strip()
        f.close()
        contents = contents.split("\n")
        for j in range(0, len(contents)): 
            try:  
                contents[j] = contents[j].split(": ")[1] 
            except: 
                contents[j] = contents[j]

        state=contents[1]

        if state=="RUNNING":
            list_html += """
                         <h3> <a href={0}>{1}</a> </h3>
                         <form action="/edit">
                             <input type='hidden' name='NAME' value='{1}'/>
                             <button type='submit' name='ACTION' value='poweron' disabled>Power on</button>
                             <button type='submit' name='ACTION' value='poweroff'>Power off</button>
                             <button type='submit' name='ACTION' value='delete'>DELETE</button>
                         </form>
                         <br> </br>""".format("static/" + i + "/" + os.listdir("static/" + i)[0], i)
        elif state=="OFF":
            list_html += """
                         <h3> <a href={0}>{1}</a> </h3>
                         <form action="/edit">
                             <input type='hidden' name='NAME' value='{1}'/>
                             <button type='submit' name='ACTION' value='poweron'>Power on</button>
                             <button type='submit' name='ACTION' value='poweroff' disabled>Power off</button>
                             <button type='submit' name='ACTION' value='delete'>DELETE</button>
                         </form>
                         <br> </br>""".format("static/" + i + "/" + os.listdir("static/" + i)[0], i)

        elif state=="PROVISIONING":
            list_html += """
                         <h3>{0} (CURRENTLY PROVISIONING)</h3>
                         <form action="/edit">
                             <input type='hidden' name='NAME' value='{0}'/>
                             <button type='submit' name='ACTION' value='delete'>DELETE</button>
                         </form>
                         <br> </br>""".format(i)

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
    
    # Getting action and VM name using flask session tokens
    action = request.args.get('ACTION')
    name = request.args.get('NAME')

    # Running different code based on the requested action
    if action == "delete":
        subprocess.run("{{{DIREC}}}/VMEXE/dvm.sh \"{0}\" >> error_{0}.log 2>&1".format(name), shell = True, stdout=subprocess.PIPE)

    if action == "poweron":
        subprocess.run("vboxmanage startvm \"{0}\" --type headless; sed -i 's/STATE: OFF/STATE: RUNNING/g' \"{{{DIREC}}}/VMS/{0}/details.txt\" >> error_{0}.log 2>&1".format(name), shell = True, stdout=subprocess.PIPE)

    if action == "poweroff":
        subprocess.run("vboxmanage controlvm \"{0}\" poweroff; sed -i 's/STATE: RUNNING/STATE: OFF/g' \"{{{DIREC}}}/VMS/{0}/details.txt\" >> error_{0}.log 2>&1".format(name), shell = True, stdout=subprocess.PIPE)

    return redirect("/select")
 
if __name__ == "__main__":
    # Making a session key for each user to set session tokens correctly
    app.secret_key = os.urandom(12)

    # Setting the IP address and port for the flask server to run on
    app.run(host='{{{ADDRESS}}}', port={{{PORT}}})
