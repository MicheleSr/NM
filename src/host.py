#! /usr/bin/env python

"""
Framework di monitoraggio della rete
Modulo che fornisce le informazioni relative a un host
"""

from threading import Thread
from scan import scan_host
from time import sleep
from sys import exit

class Host(Thread):

    def __init__(self, ip):

        """ Costruttore del thread """

        # chiamata al costruttore della superclasse 
        Thread.__init__(self)
        # per farlo terminare in caso di terminazione del main
        self.setDaemon(True)
        # dizionario contentente le informazioni sull'host
        self.info = {
            'ip': ip,
            'isUp': True,
        }


    def run(self):

       """
       Metodo run del thread, eseguito alla chiamata di start().
       Finche' non viene richiesta l'interruzione, continua a 
       effettuare scansioni sull'host per ricercarne i servizi.
       """

       try:
           while(True):
               # aggiorna le info sul thread
               self.getResults()

               # attendi 30 secondi
               sleep(30)
       except:
           exit()
       

    def getResults(self):

        """
        Aggiorna le informazioni contenute nel dizionario 
        dell'host utilizzando nmap per la ricerca dei servizi
        e per la determinazione dello stato dell'host (up/down). 
        """

        ip = self.info['ip']

        # ricerca i servizi nell'host
        results = scan_host(ip)

        # dai risultati della ricerca determiniamo lo stato dell'host
        isUp = ip in results.all_hosts() and results[ip].state() == 'up' 

        # se l'host e' attivo inseriamo i vari servizi in un dizionario
        if isUp:

            services = {
                'tcp': [[y,
                    results[ip].tcp(y)['state'], results[ip].tcp(y)['name'],
                    results[ip].tcp(y)['product'], results[ip].tcp(y)['version']]
                    for y in results[ip].all_tcp()
                ],

                'udp': [[y,
                    results[ip].udp(y)['state'], results[ip].udp(y)['name'], 
                    results[ip].udp(y)['product'], results[ip].udp(y)['version']]
                    for y in results[ip].all_udp()
                ],

                'ip': [[y,
                    results[ip].ip(y)['state'], results[ip].ip(y)['name'], 
                    results[ip].ip(y)['product'], results[ip].ip(y)['version']]
                    for y in results[ip].all_ip()
                ],

                'sctp': [[y,
                    results[ip].sctp(y)['state'], results[ip].sctp(y)['name'], 
                    results[ip].sctp(y)['product'], results[ip].sctp(y)['version']]
                    for y in results[ip].all_sctp()
                ],
            }

        else:
            services = None

        self.info =  {
            'ip': ip, 
            'isUp': isUp, 
            'services': services 
        }
