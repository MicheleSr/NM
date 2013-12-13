#! /usr/bin/env python

"""
Framework per il monitoraggio della rete
Modulo per la scansione multithread della rete
"""

from threading import Thread
from addresses import get_network_address
from scan import host_discovery 
from host import Host
from time import sleep
from sys import argv, exit

# classe che rappresenta il motore della scansione
class NetMapper(Thread):

    # costruttore
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True) 
        self.threads = []

    def run(self):

        """
        Metodo run del thread, viene richiamato tramite start().
        Viene eseguito un loop che cerca a intervalli di 30 secondi
        nuovi hosts sulla rete e per ogni host che trova inizializza
        un thread che ne raccoglie le informazioni.
        I vari thread vengono raccolti all'interno di una lista.

        L'indirizzo della rete viene preso dalla linea di comando o se 
        non fornito si cerca di indovinarlo a partire dall'ip della 
        macchina (assumendo che la netmask sia 255.255.255.0 
        come spesso si verifica). 
        """

        self.known_hosts = []

        if '-n' in argv: 
            network_address = argv[argv.index('-n') + 1]

        elif '--network' in argv: 
            network_address = argv[argv.index('--network') + 1]

        else: 
            network_address = get_network_address()
        if not network_address:
            print("Cannot find network address... program will continue without network scanning!\n" +
                  "If this trouble persist, try providing the network address in the launch command!\n" +
                  "Press CTRL-C to terminate!")
            exit()

        while(True):

            hosts = host_discovery(network_address) 

            for host in hosts:
                if not (host in self.known_hosts):
                    self.known_hosts.append(host) 
                    print("Starting thread for host %s" % host) 
                    thread = Host(host)
                    self.threads.append(thread)
                    thread.start()

            for thread in self.threads:
                if not thread.is_alive:
                    self.known_hosts.remove(thread.info['ip'])

            sleep(30)

