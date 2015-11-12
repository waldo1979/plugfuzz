#!/usr/bin/python
import os.path
import web
import sqlite3
import threading

from fuzz import Fuzzer 

####################
# RESULTS IDENTIFIER
# 0 = not loaded
# 1 = loaded no errors
# 2 = crashed
# 3 = hung

#### Web API ####
counter = 0
lock = threading.Lock()

#class start_test:
#    def GET(self):
#        raise web.seeother("/test/"+str(counter)+"/payload")

class get_nextid():
    def GET(self):
        return counter

class get_payload():
    def GET(self,testnum):
        global counter
        global lock
        testcase_tmpl = web.template.frender("testcase.html")
        payload_top = str(testcase_tmpl(testnum))
        payload_bottom = "\n</body></html>"
        try:
            lock.acquire(True)
            payload_body = Fuzzer.Instance().get_next()
            cur.execute("INSERT INTO testcases (id,result,payload) VALUES (?,?,?)", (testnum,str(0), buffer(payload_body)))
            counter+=1
        finally:
            lock.release()

        return (payload_top + payload_body + payload_bottom)

class mark_loaded():
    def GET(self, testnum):
        global lock
        try:
            lock.acquire(True)
            #cur = conn.cursor()
            cur.execute("SELECT count(id) FROM testcases WHERE id = ?", (testnum,))
            row = cur.fetchone()
            if (row is not None):
                cur.execute("UPDATE testcases SET result = 1 WHERE id = ?", (testnum,))
                conn.commit()
        finally:
            lock.release()
        
        return counter

class mark_hung():
    def GET(self, testnum):
        global lock
        try:
            lock.acquire(True)
            #cur = conn.cursor()
            cur.execute("SELECT count(id) FROM testcases WHERE id = ?", (testnum,))
            row = cur.fetchone()
            if (row is not None):
                cur.execute("UPDATE testcases SET result = 3 WHERE id = ?", (testnum,))
                conn.commit()
        finally:
            lock.release()
        
        return counter


class get_status():
    def GET(self, testnum):
        global lock
        try:
            lock.acquire(True)
            cur.execute("SELECT result FROM testcases WHERE id = ?", (testnum,))
            row = cur.fetchone()
        finally:
            lock.release()
        
        if row is None:
            return -1
        else:
            return row[0]

class record_crash():
    def POST(self, testnum):
        pass

urls = (
    "/getnextid", "get_nextid",
    "/test/(\d+)/payload", "get_payload",
    "/test/(\d+)/loaded", "mark_loaded",
    "/test/(\d+)/hunt", "mark_hung",
    "/test/(\d+)/status", "get_status"
    #"/test/(\d+)/record_crash","record_crash"
)

app = web.application(urls, globals())
conn = sqlite3.connect("state.db", check_same_thread=False)
cur = conn.cursor()

def db_setup():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='testcases';")
    row = cur.fetchone()
    if (row is None):
        cur.execute("CREATE TABLE testcases (id int, result int, payload blob)")
        conn.commit()
    else:
        pass

if __name__ == '__main__':
    db_setup()
    app.run()
