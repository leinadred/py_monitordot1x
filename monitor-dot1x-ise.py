#!/usr/bin/env python3
# Daniel Meier - 2021 04 24
# Very simple (!) to monitor Dot1X / Radius Response, no Challenge-Response
######################################################################

import radius
import logging
import time
import argparse
import socket
######################################################################
# Nagios (and forks) return values
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

######################################################################

parser = argparse.ArgumentParser()
args_mode = parser.add_mutually_exclusive_group(required=True)
args_mode.add_argument("--nagios", action="store_true",help="NAGIOS compatible return (0-4 state and detailed output")
args_mode.add_argument("--zabbix", action="store_true",help="ZABBIX compatible return (0-2 state and no detailed output")

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

r = radius.Radius(args.key, host=args.host, port=args.port)

def fun_auth():
    global v_result
    global v_latency
    
    starttime=time.time()
    v_result=r.authenticate(args.user, args.password)
    v_latency=time.time()-starttime
def fun_out():
    global v_result
    global v_latency

    if args.simple:
        try:
            v_result==True
        except:
            print("0")
        else:
            print("1")
    else:
        try:
            v_result==True
        except:
            print("CRITICAL! Check failed! Authentication not possible!")
            raise SystemExit(CRITICAL)
        else:
            print("OK! - Latency: "+str(v_latency)+" seconds")
            raise SystemExit(OK)


if __name__ == "__main__":
    fun_auth()
    fun_out()
