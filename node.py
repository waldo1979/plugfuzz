#!/usr/bin/python
import os,sys
import subprocess
import time
sys.path.append("../pydbg")

from pydbg import *
global debug

#import http.client
#import httplib
import requests

last_testid = 0
attempts = 0

def m_conmsg(message, indent):
    sys.stdout.write("  "* indent) 
    if indent > 0:
        sys.stdout.write("- "+message+"... ")
    else:
        sys.stdout.write("[*] "+message+"... ")

def get_nextid():
    global last_testid
    m_conmsg("Getting next test id", 0)
    r = requests.get("http://localhost:8081/getnextid")
    last_testid = r.text
    print last_testid

def not_loaded(testid):
    global attempts
    m_conmsg("Checking page loaded", 1)
    r = requests.get("http://localhost:8081/test/%s/status" % testid)
    response = r.text
    if attempts == 3:
        print "FAILED TO LOAD"
        # TODO LOG FAILURE
        attempts = 0
        return False
    elif response == "0":
        attempts += 1
        print "NOT LOADED"
        return True 
    elif response == "-1":     
        attempts += 1
        print "NOT LOADED"
        return True 
    elif response == "1":
        attempts = 0
        print "LOADED"
        return False
    else:
        print "EPIC FAILURE"
        return True


def test_loop():
    start_safari()
    while(1):
        load_test()


def start_safari():
    ## TODO
    # Set Heap Debugging environmental variables
    debug = pydbg()
    m_conmsg("Starting Safari",0)
    safari_process = subprocess.Popen(['/Applications/Safari.app/Contents/MacOS/SafariForWebKitDevelopment', ''], env=dict(os.environ, DYLD_INSERT_LIBRARIES="/usr/lib/libgmalloc.dylib"), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    debug.attach(safari_process.pid)
    print "DONE"
    time.sleep(1)
    m_ascript('tell application "Safari" to close every window') 
    m_ascript('tell application "Safari" to open location "about:blank"') 


def load_test():
    get_nextid()
    current_id = last_testid
    m_ascript('tell application "Safari" to set the URL of the front document to "http://localhost:8081/test/' + str(current_id) + '/payload"')
    while(not_loaded(current_id)):
        time.sleep(1)

def m_ascript(ascript):
    osa = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return osa.communicate(ascript)[0]

def handler_crash(pydbg):
    context = pydbg.dump_context()

def main():
    test_loop()

if __name__ == '__main__':
    main() 
