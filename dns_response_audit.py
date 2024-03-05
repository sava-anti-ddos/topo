# Run at h5, aduit received DNS responses and normal traffic

from scapy.all import *
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP
import time
import signal
import sys

# counter for the number of DNS responses
DNS_PACKETS_COUNTER = 0
# counter for the number of bytes received
DNS_BYTES_COUNTER = 0
# list to store the traffic packets with tag
PACKETS = []
# the path of the file to save the traffic
AUDIT_TRAFIC_FILE = "audit/audit_traffic.csv"

# aduit the DNS responses and normal traffic
def attack_audit(pkt):
    global PACKETS
    # check if the packet is a DNS response
    if pkt.haslayer(DNS) and pkt[DNS].qr == 1:
        global DNS_PACKETS_COUNTER
        global DNS_BYTES_COUNTER

        # record the DNS response
        DNS_PACKETS_COUNTER += 1
        DNS_BYTES_COUNTER += len(pkt)
        PACKETS.append({'time': time.time(), 'packet_size': len(pkt), 
                              'source_ip': pkt[IP].src, 'destination_ip': pkt[IP].dst, 
                              'protocol': pkt[IP].proto,
                              'tag': 'DNS_RESPONSE'})
        
        print("DNS response count: {}, bytes: {}, total bytes: {}"
              .format(DNS_PACKETS_COUNTER, len(pkt), DNS_BYTES_COUNTER))
    elif pkt.haslayer(IP):
        # record normal traffic
        PACKETS.append({'time': time.time(), 'packet_size': len(pkt), 
                              'source_ip': pkt[IP].src, 'destination_ip': pkt[IP].dst, 
                              'protocol': pkt[IP].proto,
                              'tag': 'NORMAL'})


# handle Ctrl+C to print the audit results and save the DNS responses to a file
def signal_handler(sig, frame):
    print("Audit results:")
    print("Number of DNS responses received: {}".format(DNS_PACKETS_COUNTER))
    print("Total bytes received: {}bytes".format(DNS_BYTES_COUNTER))

    # Save the packets to a file
    if not os.path.exists(os.path.dirname(AUDIT_TRAFIC_FILE)):
        os.makedirs(os.path.dirname(AUDIT_TRAFIC_FILE))
    with open(AUDIT_TRAFIC_FILE, 'a') as f:
        # write the header if the file is empty
        if os.stat(AUDIT_TRAFIC_FILE).st_size == 0:
            f.write('time,packet_size,source_ip,destination_ip,protocol,tag\n')
        for pkt in PACKETS:
            f.write(f"{pkt['time']},{pkt['packet_size']},{pkt['source_ip']},{pkt['destination_ip']},{pkt['protocol']},{pkt['tag']}\n")
        print(f"DNS responses and normal traffic saved to {AUDIT_TRAFIC_FILE}")

    sys.exit(0)

if __name__ == "__main__":
    # handle Ctrl+C to print the audit results and save the DNS responses to a file
    signal.signal(signal.SIGINT, signal_handler)

    # sniff inbound traffic
    sniff(prn=attack_audit, filter='inbound', store=0)
