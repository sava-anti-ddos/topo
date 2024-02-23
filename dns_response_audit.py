# Run at h5

from scapy.all import *
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP
import time
import signal
import sys

# counter for the number of DNS responses
PACKETS_COUNTER = 0
# counter for the number of bytes received
BYTES_COUNTER = 0
# list to store the DNS responses
DNS_RESPONSES = []
# the path of the file to save the DNS responses
DNS_RESPONSES_FILE = "audit/dns_responses.csv"


# detect DNS reflection attack
def attack_audit(pkt):
    # check if the packet is a DNS response
    if pkt.haslayer(DNS) and pkt[DNS].qr == 1:
        global PACKETS_COUNTER
        global BYTES_COUNTER
        global DNS_RESPONSES

        # record the DNS response
        PACKETS_COUNTER += 1
        BYTES_COUNTER += len(pkt)
        DNS_RESPONSES.append({'time': time.time(), 'response_size': len(pkt), 
                              'query_name': pkt[DNSQR].qname, 'query_type': pkt[DNSQR].qtype,
                              'source_ip': pkt[IP].src, 'destination_ip': pkt[IP].dst, 
                              'source_port': pkt[UDP].sport, 'destination_port': pkt[UDP].dport,})
        
        print("DNS response count: {}, bytes: {}, total bytes: {}"
              .format(PACKETS_COUNTER, len(pkt), BYTES_COUNTER))

# handle Ctrl+C to print the audit results and save the DNS responses to a file
def signal_handler(sig, frame):
    print("Audit results:")
    print("Number of DNS responses received: {}".format(PACKETS_COUNTER))
    print("Total bytes received: {}bytes".format(BYTES_COUNTER))

    # Save the DNS responses to a file
    if not os.path.exists(os.path.dirname(DNS_RESPONSES_FILE)):
        os.makedirs(os.path.dirname(DNS_RESPONSES_FILE))

    with open('audit/dns_responses.csv', 'w') as f:
        f.write('time,response_size,query_name,query_type,source_ip,destination_ip,source_port,destination_port\n')
        for response in DNS_RESPONSES:
            f.write('{},{},{},{},{},{},{},{}\n'.format(
                response['time'], response['response_size'], response['query_name'], response['query_type'],
                response['source_ip'], response['destination_ip'], response['source_port'], response['destination_port']))
    sys.exit(0)

if __name__ == "__main__":
    # handle Ctrl+C to print the audit results and save the DNS responses to a file
    signal.signal(signal.SIGINT, signal_handler)

    sniff(prn=attack_audit, filter="udp", store=0)
