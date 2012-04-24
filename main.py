#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import Cookie
import os
from os import sep, curdir
import cgi
import hashlib

def saveposttofile(postdata):
    if not os.path.exists("cache"):
        os.makedirs("cache")
    if not os.path.exists("cache/posts"):
        os.makedirs("cache/posts")
    post = open("cache/posts/" + hashlib.sha224(postdata).hexdigest(), "w")
    print postdata
    post.write(postdata)
    post.close()

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print "getting"

        if self.path.find("?") > 0:
            self.path, commands = self.path.split("?",1)
            postitems = commands.replace("&","\n")
            saveposttofile(postitems)

        if "Cookie" in self.headers:
            c = Cookie.SimpleCookie(self.headers["Cookie"])
            cookie = c["username"].value
            #self.send_response(200)
            #self.send_header('Content-type',	'text/html')
            #self.end_headers()
            #self.wfile.write(cookie)

        if self.path.startswith("/wall"):
            f = open(curdir + sep + "res/postmessage.html")
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            self.wfile.write(f.read())

        elif self.path.endswith(".html"):
            f = open(curdir + sep + "res" + self.path)
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            self.wfile.write(f.read())

        elif self.path.endswith(".js"):
            f = open(curdir + sep + "res" + self.path)
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            self.wfile.write(f.read())


    def do_POST(self):
        if "Cookie" in self.headers:
            c = Cookie.SimpleCookie(self.headers["Cookie"])
            username = c["username"].value
            userid = c["userid"].value
            pwhash = c["pwhash"].value


        print "posting"
        content, parts = cgi.parse_header(self.headers.getheader('content-type'))
        if content == 'multipart/form-data':
            query = cgi.parse_multipart(self.rfile, parts)

        createusername = query.get('createusername[]')
        postcontent = query.get('postcontent[]')

        if (postcontent):
            print "HIIIIIIIIIIIII"
            print username
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers
            self.wfile.write(('username = ', username, '/n'))
            self.wfile.write(('userid = ', userid, '/n'))
            self.wfile.write(('pwhash = ', pwhash, '/n/n'))
            self.wfile.write(('post content = ', postcontent[0], '/n/n'))
            nextkey = hashlib.sha224(postcontent[0]+pwhash).hexdigest()
            self.wfile.write(('next post key = ',nextkey))

            postdata = 'username = ' + username + '\nuserid = ' + userid + '\npassword hash = ' + pwhash
            postdata = postdata + '\n\npost content = ' + postcontent[0]

            nextkey = hashlib.sha224(postcontent[0]+pwhash).hexdigest()
            postdata = postdata +'next post key = ' + nextkey

            #save file


            print "done"

        if (createusername):
            print createusername[0]
            newuserhash = hashlib.sha224(createusername[0]).hexdigest()
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.send_header('Set-Cookie','userid='+newuserhash+'; Expires=Tue, 23-Dec-2012 00:00:00 GMT')
            self.send_header('Set-Cookie','username='+createusername[0]+'; Expires=Tue, 23-Dec-2012 00:00:00 GMT')
            self.send_header('Set-Cookie','pwhash='+hashlib.sha224(createusername[1]).hexdigest()+'; Expires=Tue, 23-Dec-2012 00:00:00 GMT')
            self.end_headers()
            self.wfile.write('<script type="text/javascript">self.location="/";</script>')
            print newuserhash



def main():
    try:
        server = HTTPServer(('', 8080), MyHandler)
        print 'started server'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()