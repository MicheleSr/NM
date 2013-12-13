#! /usr/bin/env python

""" 
Framework di monitoraggio della rete
Modulo che fornisce le funzioni di ricerca e scansione 

N.B: utilizza nmap... e' necessario che il software nmap
sia installato nella macchina. Nmap e' un software open-source,
l'ultima versione e' disponibile all'indirizzo http://nmap.org/
Inoltre e' necessario installare il modulo del python nmap (ad
esempio tramite un gestore di moduli come pip o easy_install)
"""
from nmap import PortScanner 


def host_discovery(network_address):

    """
    Tramite il modulo nmap viene effettuata una ricerca degli host
    attivi in rete. Ritorna una lista degli host attivi in rete.
    """

    scanner = PortScanner()

    if network_address:
        print("Searching for hosts on %s..." % network_address)

    scanner.scan(hosts=network_address, arguments='-sP')

    iplist = [ip for ip in scanner.all_hosts() 
              if scanner[ip].state() == 'up']

    print("Found %s host(s)" % len(iplist))
    print(iplist)

    return iplist


def scan_host(host):

    """ 
    Utilizza nmap per ricercare i servizi sull'host... la scansione e' 
    di tipo probing, nel senso che effettua delle prove sulle varie 
    porte per determinare il tipo di servizio, ritorna un oggetto
    contenente i risultati sulla scansione (che tra l'altro e' l'oggetto
    stesso che contiene il metodo per la scansione) 
    """

    scanner = PortScanner()
    print("Checking services on %s" % host)
    scanner.scan(hosts=host, 
                 arguments='--host_timeout 60s -sV --version_light')

    return(scanner)
