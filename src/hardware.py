#! /usr/bin/env python

from threading import Thread
from sys import exit
from time import sleep
from psutil import cpu_percent, virtual_memory, swap_memory, \
                   net_io_counters, disk_io_counters

"""
Framework di monitoraggio della rete
Modulo per le risorse hardware 

Questo modulo si occupa di ottenere dal sistema operativo lo stato delle
risorse hardware, e in particolare:

- utilizzo cpu;
- utilizzo della memoria centrale;
- utilizzo dello swap;
- utilizzo del disco in lettura e scrittura;
- banda di rete in entrata e uscita.

Questo modulo utilizza la libreria esterna psutil, installabile tramite 
un gestore di pacchetti python come PIP (Alternative Python Package 
Installer). 
"""

class Hardware(Thread):

    def __init__(self):

        """
        Costruttore del Thread, inizializza il thread, lo setta
        come demone e inizializza gli attributi dell'oggetto
        """

        Thread.__init__(self)
        self.setDaemon(True)
        self.cpu=0
        self.cores = len(cpu_percent(percpu=True))
        self.ram=0
        self.total_ram = virtual_memory().total
        self.swap=0
        self.total_swap = swap_memory().total
        self.read=0
        self.write=0
        self.net_in=0
        self.net_out=0


    def run(self):

        """
        Metodo run del thread, raccoglie in tempo reale le informazioni
        sull'hardware tramite psutil.
        """

        try:
            while True:
     
                # disk, net (temp)
                self.read_tmp = disk_io_counters().read_bytes
                self.write_tmp = disk_io_counters().write_bytes

                self.net_in_tmp = net_io_counters().bytes_recv
                self.net_out_tmp = net_io_counters().bytes_sent

                # cpu
                self.cpu = cpu_percent(interval=1)

                # disk
                self.read = \
                    disk_io_counters().read_bytes - self.read_tmp
                self.write = \
                    disk_io_counters().write_bytes - self.write_tmp

                # net
                self.net_in = \
                    net_io_counters().bytes_recv - self.net_in_tmp
                self.net_out = \
                    net_io_counters().bytes_sent - self.net_out_tmp

                # memories
                self.ram = virtual_memory().percent
                self.swap = swap_memory().percent

                sleep(1) 

        except: 
            exit()


    def get_results(self):

        """ 
        Restituisce le informazioni sull'hardware sotto forma 
        di dizionario 
        """

        return {
            'cpu': self.cpu,
            'cores': self.cores,
            'ram': self.ram,
            'total_ram': self.total_ram,
            'swap': self.swap,
            'total_swap': self.total_swap,
            'disk_r': self.read,
            'disk_w': self.write,
            'net_in': self.net_in,
            'net_out': self.net_out,
        }

