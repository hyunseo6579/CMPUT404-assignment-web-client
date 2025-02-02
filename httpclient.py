#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import json
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def get_host_port(self,url):
        host = urllib.parse.urlparse(url).hostname
        port = urllib.parse.urlparse(url).port
        if port is None:
            port = 80
        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        first_line = data.split("\r\n")[0]
        code = first_line.split(" ")[1]
        return int(code)

    def get_headers(self,data):
        # return everything after first line until \r\n\r\n
        headers = []
        temp = data.split("\r\n")
        temp.pop(0)
        temp = temp[:temp.index('')]
        for eachHeader in temp:
            headers.append(eachHeader.split(': ', 1))
        return headers

    def get_body(self, data):
        # return everything after \r\n\r\n
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        try:
            return buffer.decode('utf-8')
        # reference: https://stackoverflow.com/a/19706723
        except UnicodeDecodeError:
            return buffer.decode('ISO-8859-1')

    # assemble and return request; referenced Class Participation Exercise: HTTP GET
    # reference2: https://www.ietf.org/rfc/rfc2616.txt
    def assemble(self, host, path, method, body=None):
        # 1 == GET, 2 == POST
        if method == 1:
            request = "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\nAccept: */*\r\n\r\n" % (path, host)
        else:
            request = "POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %s\r\nConnection: close\r\nAccept: */*\r\n\r\n" % (path, host, str(len(body)))
            if len(body) is not 0:
                request += body
        return request

    def GET(self, url, args=None):
        host, port = self.get_host_port(url)
        self.connect(host,port)
        path = urllib.parse.urlparse(url).path
        if path == "":
            path = "/"

        request = self.assemble(host, path, 1)
        self.sendall(request)

        data = self.recvall(self.socket)

        code = self.get_code(data)
        body = self.get_body(data)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        self.connect(host,port)
        path = urllib.parse.urlparse(url).path
        if path == "":
            path = "/"

        # needs to be in format of: a=b&fruit=apple ...
        # reference: https://www.w3schools.com/python/gloss_python_loop_dictionary_items.asp
        post_content = ''
        if args is not None:
            for key in args:
                post_content += str(key)+"="+str(args[key])+"&"
            # remove last '&'
            post_content = post_content[:-1]

        request = self.assemble(host, path, 2, post_content)
        self.sendall(request)

        data = self.recvall(self.socket)

        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
