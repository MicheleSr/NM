NM
==

Network Monitor v0.1: this software gives information about the machine 
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
