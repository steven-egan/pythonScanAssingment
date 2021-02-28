#!/usr/bin/python3
import socket
import sys
import argparse
import logging
from os import path
import json
import requests

#Setup
parser=argparse.ArgumentParser()

parser.add_argument('--ofl', help='Absolute path for output', type=str)
parser.add_argument('--ifl', help='Absolute path for input', type=str)
parser.add_argument('--hl', help='Comma delimeted host list', type=str)
parser.add_argument('--pl', help='Comma delimeted port list', type=str)
parser.add_argument('--udp', help='Use UDP [1|0]', default=0, type=str)
parser.add_argument('--wh', help='Send to webhook', type=str)

args=parser.parse_args()

#Set logger
logging.basicConfig(
    level=logging.getLevelName(logging.DEBUG), 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=args.ofl
)

def scan():
    data = {}
    if(path.exists(args.ifl)):
        with open(args.ifl) as input_file:
            data = json.load(input_file)
            logging.info("Running with the following", data)
    else:
        data["hostsList"] = args.hl.split(",")
        data["portList"] = {}
        data["portList"]["startPort"] = None
        data["portList"]["endPort"] = None
        data["portList"]["otherPorts"] = args.pl.split(",")
    
    # Run inputs
    for host in data["hostList"]:
        scanHost(host, data["portList"])

    # Send to webhook 
    if(args.wh):
        # Open file and get data
        with open(args.ofl,'rb') as filedata:
            r = requests.post(args.wh, files={'file': filedata})
        
def scanHost(ip, data):
    startPort = data["startPort"]
    endPort = data["endPort"]
    otherPorts = data["otherPorts"]
    logging.info('[*] Starting port scan on host %s' % ip)

    # Begin port scan on host
    port_scan(ip, startPort, endPort )
    for port in otherPorts:
        port_scan(ip, port, port)

    logging.info('[+] port scan on host %s complete' % ip)



def port_scan(ip, startPort, endPort):
    use_udp = args.udp == "1"

    for port in range(startPort, endPort + 1):
        try:
            # Create a new socket us socket.SOCK_DGRAM for UDP
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM if not use_udp else socket.SOCK_DGRAM)
            
            # Print if the port is open
            if use_udp == False and not connection.connect_ex((ip, port)):
                loggin.info(f'[+] TCP connection open on {ip}:{port}')

            if use_udp:
                connection.sendto("Hello".encode(), (ip, port))
                logging.info(f'[+] Sent Hello packet to {ip}:{port}')
            connection.close()
                
        except Exception as e:
            logging.error(e)
            pass


if __name__ == '__main__':
    socket.setdefaulttimeout(0.01)

    if len(sys.argv) < 2:
        print('Please use the -h command to see the options available')
    
    # Complete the scan
    scan()