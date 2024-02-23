## Project Structure

- net.py: labs topo

- main.py: net.py usage

- conf/: each router BGP and OSPF config

## Requirements

- mininet

  - Install mininet follow the [official website](https://mininet.org/download/), VM installation is recommended. 

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