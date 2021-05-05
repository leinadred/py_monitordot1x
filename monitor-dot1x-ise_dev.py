#!/usr/bin/env python3
# Daniel Meier - 2021 04 24
# Very simple (!) to monitor Dot1X / Radius Response, no Challenge-Response
######################################################################

from __future__ import print_function
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet
import logging
import time
import argparse
import socket
import random
import sys
######################################################################
# Nagios (and forks) return values
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

######################################################################

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--simple", action="store_true",help="only return 0/1 for Success or Failure (i.e. Zabbix uses only 0/1)", default=False)
parser.add_argument("-l", "--latency", help="only return latency", default=False)
parser.add_argument("-a", "--anyresponse", action="store_true", help="Any response is good. Reject or Accept", default=False)
parser.add_argument("-H", "--host", help="Hosts address to authenticate with", required=True)
parser.add_argument("-K", "--key", help="Preshared Key to use with the authenticating server", required=True)
parser.add_argument("-U", "--user", help="Username to authenticate with", required=True)
parser.add_argument("-P", "--password", help="Usernames password to authenticate with", required=False)
parser.add_argument("-p", "--port", help="UDP Port to use (defaults to 1812)", default="1812")
parser.add_argument("-v", "--verbose", action="store_true", help="detailed informations", default=False)
parser.add_argument("-vv", "--verbose2", action="store_true", help="detailed informations", default=False)


args = parser.parse_args()

try:
    socket.gethostbyname(args.host)
except:
    print("Please check given host! no valid IP or resolvable server name found!")
else:
    pass

if args.verbose:
    logging.basicConfig( level=logging.WARN)

if args.verbose2:
    logging.basicConfig( level=logging.DEBUG)

def fun_auth():
    global v_result
    global v_latency
    global reply
    starttime=time.time()
    def_server = Client(server=args.host, secret=args.key.encode('ascii'), dict=Dictionary("dictionary"))

# create request
    req = def_server.CreateAuthPacket(code=pyrad.packet.AccessRequest,User_Name=args.user, NAS_Identifier="localhost")
    req["User-Password"] = req.PwCrypt()

# send request
    reply = def_server.SendPacket(req)

    if reply.code == pyrad.packet.AccessAccept:
        print("access accepted")
    else:
        print("access denied")
    v_latency=time.time()-starttime

    print("Attributes returned by server:")
    for i in reply.keys():
        print("%s: %s" % (i, reply[i]))

def SendPacket(def_server, req):
    try:
        def_server.SendPacket(req)
    except pyrad.client.Timeout:
        print("RADIUS server does not reply")
        sys.exit(1)
    except socket.error as error:
        print("Network error: " + error[1])
        sys.exit(1)

def fun_out():
    global v_result
    global v_latency
    global reply
    if args.simple:
        if reply.code == pyrad.packet.AccessAccept:
            print("1")
        else:
            print("0")
    else:
        try:
            reply.code == pyrad.packet.AccessAccept
        except:
            print("CRITICAL! Check failed! Authentication not possible!")
            raise SystemExit(CRITICAL)
        else:
            print("OK! - Latency: "+str(v_latency)+" seconds")
            raise SystemExit(OK)


if __name__ == "__main__":
    fun_auth()
    fun_out()
