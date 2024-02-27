## Project Structure

- net.py: labs topo

- log.py: custom logger

- main.py: net.py usage

- dns_query_attack.py: dns reflection attack simulation using multiple threads

- dns_response_audit.py: dns reflection attack victim side audit

- attack_visualization.py: dns reflection attack visualization

- random_http_request.py: background traffic simulation

- conf/: each router BGP and OSPF config

- requirements.txt: required python packages

## Requirements

- mininet

  - Install mininet follow the [official website](https://mininet.org/download/), VM installation is recommended. 

  - or, install mininet using apt:

    ```
    sudo apt install mininet
    ```


- quagga

  - Install quagga:

    ```
    sudo apt install quagga
    ```

- dnsmasq

  - Install dnsmasq:

    ```
    sudo apt install dnsmasq
    ```

  - Edit /etc/dnsmasq.conf:

    ```
    # bind h4-eth0 after net start
    bind-dynamic
    # provide dns service for local and other network machines
    listen-address=127.0.0.1,127.0.0.53,30.30.10.10
    # upstream dns server
    server=8.8.8.8
    ```
    
   - Stop the systemd-resolved service:

     ```
     sudo systemctl stop systemd-resolved
     ```

   - Restart dnsmasq service:

     ```
     sudo systemctl restart dnsmasq
     ```

- Additional Python packages:

  - scapy
  - pandas
  - matplotlib