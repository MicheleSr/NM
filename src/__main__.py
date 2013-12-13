#! /usr/bin/env python

from sys import argv, version
from netmapping import NetMapper
from netstat import netstat 
from hardware import Hardware
from json import dumps 
from pkgutil import get_data

"""
Framework di monitoraggio della rete
Modulo main e webserver del programma 

Questo e' il modulo dove il programma inizia, il suo compito
e avviare i vari thread e agire da webserver ascoltando 
su una data porta TCP (o sulla 8080 di default)
"""

if version[0] == '3':
    from http.server import HTTPServer, BaseHTTPRequestHandler
else: 
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    FileNotFoundError = IOError

HELP_MSG = """
usage: -p,--port [port] : webserver listening TCP port (default:8080)
       -n, --network [address]: network address 
           (automatic search if not provided)
       -h, --help: show this help
       -v, --version: show information about the program
"""

VERSION_MSG = """
Net Framework v0.1: this software gives information about the machine 
and the network where it runs, such as hosts on the network and their 
services, local connections and hardware resources 
(such as CPU load, memory usage, etc...).

Information are provided with a web server that listen on a given 
TCP port (Default is 8080).

The address of the network to scan can be provided by command-line, 
if not the software will try to guess it automatically 
(it doesn't work always however).

Credits: Antonio Esposito, Michele Sorcinelli.

This software is for GNU/Linux Operating Systems. 

In order to use this program is required the nmap software:
http://nmap.org

This software is made to run with a compatible Python interpreter (such 
as CPython 2.7 or 3.3)  

Also, in order to get the program working the following python external 
modules are required:

- ipaddress
- python-nmap
- psutil

Those modules can be installed using a python package manager,
such as PIP (Alternative Python Package Installer).
"""

class MyHandler(BaseHTTPRequestHandler):

    if version[0] == '3': 
        def write(self, file):
            self.wfile.write(bytes(file, 'utf-8'))
        index = get_data('templates', 'index.html').decode('utf-8')
        style = get_data('templates', 'style.css').decode('utf-8')
        jquery = get_data('templates', 'jquery-2.0.3.min.js').decode('utf-8')

    else:
        def write(self, file):
            self.wfile.write(file)
        index = get_data('templates', 'index.html')
        style = get_data('templates', 'style.css')
        jquery = get_data('templates', 'jquery-2.0.3.min.js')

    ext_to_content_type = {
        'html': 'text/html; charset=utf-8',
        'css': 'text/css',
        'js': 'text/javascript',
        'json': 'text/json',
    }

    request_to_response = {
        'index': index,
        'style': style,
        'jquery-2': jquery,
    }


    def do_GET(self):
 
        if self.path == '/':
            self.path = '/index.html'

        request = self.path[1:].split('.')[0]
        ext = self.path.split('.')[-1]
        self.send_response(200)

        try:
            self.send_header('Content-type', self.ext_to_content_type[ext])
            self.end_headers()

            if ext == 'json':

                if request == 'hardware':
                    response = hardware.get_results()

                elif request == 'hosts':
                    response = {
                        'up': [host.info for host in netmapper.threads 
                               if host.info['isUp']],
                        'down': [host.info for host in netmapper.threads 
                                 if not host.info['isUp']],
                    }

                elif request == 'connections':
                    response = {
                        'TCP': netstat('tcp'),
                        'UDP': netstat('udp'),
                        'TCP (IPv6)': netstat('tcp6'),
                        'UDP (IPv6)': netstat('udp6'),
                    }

                self.write(dumps(response))

            else:
                self.write(self.request_to_response[request])

        except KeyError as e:
            print(e) 
            self.send_error(404)


if __name__ == '__main__':

    if '-h' in argv or '--help' in argv:
        print(HELP_MSG)
    elif '-v' in argv or '--version' in argv:
        print(VERSION_MSG)
    else:
        try:
            if '-p' in argv:
                port = int(argv[argv.index('-p') + 1])
            elif '--port' in argv:
                port = int(argv[argv.index('--port') + 1])
            else:
                port = 8080

            httpd = HTTPServer(('localhost', port), MyHandler)
            print("Starting web server on port: %d" 
                   % httpd.server_port)
            print("Press CONTROL-C for stopping it!")
            netmapper = NetMapper()
            netmapper.start()
            hardware = Hardware()
            hardware.start()
            httpd.serve_forever()

        except KeyboardInterrupt:
            print(" received, shutting down the web server\n")
            httpd.socket.close()
            exit()

        except ValueError:
            print("Error: bad launch parameters")
            exit(1)

        except Exception as e:
            print(e)

