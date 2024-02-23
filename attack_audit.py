from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, UDP

counter = 0

# detect DNS reflection attack
def attack_audit(pkt):
    # check if the packet is a DNS response
    if pkt.haslayer(DNSRR):
        global counter
        counter += 1
        print("DNS Response detected: {}, packet size: {}, bytes source IP: {}, destination IP: {}, source port: {}, destination port: {}, query name: {}, response data: {}, response length: {}".format(
    counter, len(pkt), pkt[IP].src, pkt[IP].dst, pkt[UDP].sport, pkt[UDP].dport, pkt[DNSQR].qname, pkt[DNSQR].qtype, pkt[DNSRR].type, pkt[DNSRR].rdata, pkt[DNSRR].rdlen), flush=True)

# sniff the network
sniff(prn=attack_audit, filter="udp", store=0)
