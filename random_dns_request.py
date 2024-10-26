# send dns request to the target forever

import random
import time
import sys
from scapy.layers.inet import IP, UDP
from scapy.layers.dns import DNS, DNSQR
from scapy.volatile import RandShort
from scapy.sendrecv import send

DNS_SERVER = "30.30.10.10"

QUERY_DOMAIN_OPTIONS = ["www.baid.com", "www.google.com", "www.bilibili.com", "www.bing.com"]
QUERY_TYPE = 'A'

def send_dns_request(dns_server, domain, type):
    """
    Send a DNS query to a DNS server.

    Args:
        dns_server (str): The DNS server IP address.
        domain (str): The domain to query.
        type (str): The query type.

    Returns:
        None
    """
    # generate a random DNS query ID
    query_id = random.randint(1, 65535)
    # create a DNS query packet
    dns_query = IP(dst=dns_server)/UDP(sport=RandShort(), dport=53)/DNS(id=query_id, rd=1, qd=DNSQR(qname=domain, qtype=type))
    # send the DNS query
    send(dns_query, verbose=0)

if __name__ == '__main__':
    # check the param
    if len(sys.argv) != 2:
        print('Usage: python3 random_http_request.py <interval>')
        sys.exit(1)

    interval = sys.argv[1]
    # loop forever
    while True:
        # random sleep 1 - interval
        time.sleep(random.uniform(1, int(interval)))
        # send a DNS query
        send_dns_request(DNS_SERVER, random.choice(QUERY_DOMAIN_OPTIONS), QUERY_TYPE)