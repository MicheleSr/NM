#! /usr/bin/env python

"""
Framework di monitoraggio della rete
Modulo per il controllo delle connessioni di rete sulla macchina.

Modulo sviluppato da Ricardo Pascal, ottenuto all'indirizzo web
http://voorloopnul.com/blog/a-python-netstat-in-less-than-100-lines-of-code/
e modificato per raccogliere informazioni sui protocolli udp, tcp(ipv6), 
udp(ipv6), oltre che per il protocollo tcp... questa modulo legge 
(e decodifica) le informazioni direttamente dai file forniti dal sistema
nel file system /proc

Valida per i sistemi Unix-like (Noi l'abbiamo testato su GNU/Linux).

N.B: utilizza il modulo ipaddress, installabile tramite un
gestore di moduli come pip o easy_install.
"""

from glob import glob
from re import search
from pwd import getpwuid
from os import readlink
from sys import version
from ipaddress import ip_address

# files contenenti le informazioni per ogni protocollo
files = {
    'tcp': '/proc/net/tcp',
    'udp': '/proc/net/udp',
    'tcp6': '/proc/net/tcp6',
    'udp6': '/proc/net/udp6',
}

# possibili stati delle connessioni e codifica in esadecimale 
STATE = {
    '01':'ESTABLISHED',
    '02':'SYN_SENT',
    '03':'SYN_RECV',
    '04':'FIN_WAIT1',
    '05':'FIN_WAIT2',
    '06':'TIME_WAIT',
    '07':'CLOSE',
    '08':'CLOSE_WAIT',
    '09':'LAST_ACK',
    '0A':'LISTEN',
    '0B':'CLOSING'
}

# funzione per il parsing dell'indirizzo ipv6
if version[0] == '3':
    def parse_address(ip):
        return str(ip_address(ip))
else:
    def parse_address(ip): 
        return str(ip_address(unicode(ip, 'utf-8')))


# funzione per il caricamento del file
def _load(protocol):

    # Viene letta la tabella delle connessioni e viene rimosso l'header 
    with open(files[protocol],'r') as f:
        content = f.readlines()
        content.pop(0)
    return content


# funzione per la conversione da esadecimale a intero
def _hex2dec(s):
    return str(int(s,16))


# funzione per la decodifica dell'indirizzo ip(ipv4 o ipv6)
def _ip(s, use_ipv6):

    """
    Questa funzione viene utilizzata per convertire l'indirizzo ip 
    contenuto nei file /proc/net/... nell'indirizzo ip corrispondente.
    La parte relativa all'ipv6 e' stata implementata da noi.
    
    Se viene utilizzato ipv6, e' necessario riordinare le informazioni 
    contenute nel file system proc, scambiando i gruppi da 4 a 2 a 2,
    e le coppie all'interno di ogni gruppo, infine e' necessario 
    ricomporre l'indirizzo dai blocchi, e separare i gruppi da 
    4 con ':'.

    Per quanto riguarda gli ipv4, l'algoritmo e' piu' semplice, basta 
    scomporre l'indirizzo esadecimale in gruppi da 2, convertirli in 
    intero, e ricomporli (da destra verso sinistra)
    separandoli con un '.'
    """

    if use_ipv6:

        # divido l'ipv6 in blocchi da 4
        blocks = [s[x:x+4] for x in range(0, 32, 4)] 

        # scambio i blocchi 
        for x in range(0, 8, 2):
            blocks[x], blocks[x+1] = blocks[x+1], blocks[x]

        # scambio le coppie all'interno dei blocchi 
        for i in range(len(blocks)):
            blocks[i] = (blocks[i][2:5] + blocks[i][0:2])

        # ritorno la rappresentazione corretta dell'ipv6 
        return parse_address(':'.join(blocks).lower())

    else:

        # converto le cifre esadecimali scambiando anche i blocchi
        ip = [
            (_hex2dec(s[6:8])),(_hex2dec(s[4:6])),
            (_hex2dec(s[2:4])),(_hex2dec(s[0:2]))
        ]

        # ricompongo e ritorno l'ip
        return '.'.join(ip)


# rimuove le linee vuote
def _remove_empty(array):
    return [x for x in array if x !='']


# conversione dell'ip e della porta
def _convert_ip_port(array, use_ipv6):
    host,port = array.split(':')
    return _ip(host, use_ipv6),_hex2dec(port)


# funzione per ottenere il pid del processo che utilizza la connessione
def _get_pid_of_inode(inode):

    '''
    Per ottenere il pid del processo, vengono controllati i processi 
    in esecuzione per vedere quale utilizza l'inode relativo 
    alla connessione.
    '''

    for item in glob('/proc/[0-9]*/fd/[0-9]*'):
        try:
            if search(inode,readlink(item)):
                return item.split('/')[2]
        except:
            pass
    return ''


def netstat(protocol='tcp'):

    '''
    Funzione principale, ritorna una lista contenente le informazioni 
    sulle connessioni del protocollo che gli viene passato 
    per parametro.
    '''

    content=_load(protocol)
    result = []
    use_ipv6 = (protocol == 'tcp6' or protocol == 'udp6')
    for line in content:
		
		# Separa le linee e rimuove gli spazi vuoti.
        line_array = _remove_empty(line.split(' ')) 
          
        # Converte gli indirizzi ip e le porte.            
        l_host,l_port = _convert_ip_port(line_array[1], use_ipv6) 
        r_host,r_port = _convert_ip_port(line_array[2], use_ipv6) 
        tcp_id = line_array[0]
        state = STATE[line_array[3]]
        
        # evitiamo che le udp connectionless vengono marcate 'CLOSE'                                                          
        if state == 'CLOSE' and (protocol == 'udp'                
                                 or protocol == 'udp6'):            
            state = ''
            
        # Identifica l'user dall'UID
        try:
            uid = getpwuid(int(line_array[7]))[0] 
        except KeyError:
            uid = ''
        
        # Per ottenere il pid necessitiamo dell'inode                    
        inode = line_array[9]   
        
        # Ottieniamo il pid dall'inode                                  
        pid = _get_pid_of_inode(inode)  
        
        # Cerchiamo di ottenere dal S.O. il nome del processo.                          
        try:                                                      
            exe = readlink('/proc/'+pid+'/exe')
        except:
            exe = ''

        nline = [tcp_id, uid, l_host+':'+l_port, r_host+':'
                 +r_port, state, pid, exe]
        result.append(nline)

    return result
