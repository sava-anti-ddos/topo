# Run at h5, aduit received DNS responses and normal traffic

from scapy.all import *
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP
import time
import signal
import sys
import queue

# counter for the number of DNS responses
DNS_PACKETS_COUNTER = 0
# counter for the number of bytes received
DNS_BYTES_COUNTER = 0
# list to store the traffic packets with tag
PACKETS = queue.Queue()
# the path of the file to save the traffic
AUDIT_TRAFIC_FILE = "audit/audit_traffic.csv"
# flag to indicate if the audit is finished, used to stop the write_audit_traffic thread
AUDIT_FINISHED = False


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
        PACKETS.put({'time': time.time(), 'packet_size': len(pkt), 
                              'source_ip': pkt[IP].src, 'destination_ip': pkt[IP].dst, 
                              'protocol': pkt[IP].proto,
                              'tag': 'DNS_RESPONSE'})
        
        print("DNS response count: {}, bytes: {}, total bytes: {}"
              .format(DNS_PACKETS_COUNTER, len(pkt), DNS_BYTES_COUNTER))
    elif pkt.haslayer(IP):
        # record normal traffic
        PACKETS.put({'time': time.time(), 'packet_size': len(pkt), 
                              'source_ip': pkt[IP].src, 'destination_ip': pkt[IP].dst, 
                              'protocol': pkt[IP].proto,
                              'tag': 'NORMAL'})


# thread to write the DNS responses and normal traffic to a file
def write_audit_traffic():
    if not os.path.exists(os.path.dirname(AUDIT_TRAFIC_FILE)):
        os.makedirs(os.path.dirname(AUDIT_TRAFIC_FILE))

    with open(AUDIT_TRAFIC_FILE, "a") as f:
        # write the header if the file is empty
        if os.stat(AUDIT_TRAFIC_FILE).st_size == 0:
            f.write('time,packet_size,source_ip,destination_ip,protocol,tag\n')
        while not AUDIT_FINISHED:
            try:
                pkt = PACKETS.get(block=False)
                f.write(f"{pkt['time']},{pkt['packet_size']},{pkt['source_ip']},{pkt['destination_ip']},{pkt['protocol']},{pkt['tag']}\n")
            except queue.Empty:
                time.sleep(0.5)
        print(f"Audit traffic saved to {AUDIT_TRAFIC_FILE}")


# handle Ctrl+C to print the audit results and save the DNS responses to a file
def create_signal_handler(write_audit_traffic_thread):
    def signal_handler(sig, frame):
        print("Audit results:")
        print("Number of DNS responses received: {}".format(DNS_PACKETS_COUNTER))
        print("Total bytes received: {}bytes".format(DNS_BYTES_COUNTER))

        global AUDIT_FINISHED
        AUDIT_FINISHED = True
        write_audit_traffic_thread.join()
        sys.exit(0)
    return signal_handler

if __name__ == "__main__":
    # start the thread to write the DNS responses and normal traffic to a file
    write_audit_traffic_thread = threading.Thread(target=write_audit_traffic)
    write_audit_traffic_thread.start()
    # handle Ctrl+C to print the audit results and save the DNS responses to a file
    signal.signal(signal.SIGINT, create_signal_handler(write_audit_traffic_thread))

    # sniff inbound traffic
    sniff(prn=attack_audit, filter='inbound', store=0)
