#! /usr/bin/env python

"""
Framework di monitoraggio della rete
Modulo per la gestione degli indirizzi di rete
"""

from socket import socket 

def _get_ip():

    """ 
    Questa funzione restituisce l'indirizzo ip della macchina ottenendolo 
    dal nome di una socket verso google.com. Restituisce False se si 
    verificano eccezioni (es mancanza di connessione a internet).
    """

    # inizializziamo la socket 
    s = socket()                       

    try: 
        # ci connettiamo a 'google.com'
        s.connect(('google.com', 80))  

        # prendiamo l'indirizzo dal nome della socket
        address = s.getsockname()[0]   

    except:
        # restituiamo False in caso di errore
        address = False                

    return address


def get_network_address():

    """
    Questa funzione tenta di restituire l'indirizzo di rete a partire
    dall'indirizzo ip della macchina... e' basato sul fatto che su una
    LAN generica l'indirizzo di rete e' ottenibile sostituendo l'ultima
    parte dell'ip con '0/24' (notazione CIDR). In caso l'indirizzo
    ottenuto in questa maniera non sia corretto sara' necessario utilizzare
    la linea di comando per inserire l'indirizzo manualmente.
    """

    # otteniamo l'ip della macchina
    address = _get_ip()

    # se l'indirizzo e' False ritorniamo False
    if not address:
        return False

    else:
        # dividiamo l'ip in 4 gruppi da 3 cifre
        list = address.split('.')

        # sostituiamo l'ultimo gruppo con '0/24'
        list[3] = '0/24'

        # ricomponiamo l'indirizzo finale  
        return '.'.join(list)

