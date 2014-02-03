#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle & Kris Kushniruk
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import string
# you may use urllib to encode data appropriately
import urllib
import urlparse


def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class INFO(object):
    def __init__(self,host="",port="",path="",args=""):
        self.host = host
        self.port = port
        self.path = path
        self.args = args

class HTTPClient(object):

    
    def set_request_info(self,url,args=None):

        r = urlparse.urlparse(url)

        path = r.path
        port = r.port
        params = r.params
        netloc = r.netloc
        temp = r.netloc.split(":")
        host = temp[0]

        return INFO(host.strip("\n"),port,path.strip("\n"),args)

    def connect(self, host, port):

        #no port use 80
        if port == None:
            port = 80

        #connect the client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        return client_socket

    def get_code(self, data):
        temp = data.split("\r\n")
        temp2 = temp[0].split(" ")

        return temp2[1]

    def get_headers(self,data):
        return None

    def get_body(self, data):
        temp = data.split("\r\n\r\n")
        return temp[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""

        #Grab the info from the request then open the socket
        info = self.set_request_info(url,args)

        if not info.path:
            info.path = "/"

        self.socket = self.connect(info.host,info.port)

        self.socket.sendall("GET %s HTTP/1.1\r\n" % info.path)
        self.socket.sendall("Host: %s\r\n" % info.host)
        self.socket.sendall("Connection: close\r\n")
        self.socket.sendall("\r\n")
        read = self.recvall(self.socket)


        self.socket.close()

        body = self.get_body(read)
        code = self.get_code(read)

        return HTTPRequest(int(code), body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        arg = ""

        info = self.set_request_info(url,args)

        if not info.path:
            info.path = "/"

        self.socket = self.connect(info.host,info.port)

        self.socket.sendall("POST %s HTTP/1.1\r\n" % info.path)
        self.socket.sendall("Host: %s\r\n" % info.host)
        self.socket.sendall("Content-type: application/x-www-form-encoded\r\n")
        self.socket.sendall("Connection: close\r\n")

        if args != None:
            arg = urllib.urlencode(args)
            self.socket.sendall("Content-length: %s\r\n\r\n" % str(len(arg)))
            self.socket.sendall("%s\r\n" % arg)

        self.socket.sendall("\r\n")

        read = self.recvall(self.socket)

        self.socket.close()

        code = self.get_code(read)
        body = self.get_body(read)


        return HTTPRequest(int(code), body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:      
            self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( command, sys.argv[1] )    
    



