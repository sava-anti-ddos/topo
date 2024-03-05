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

## Usage

1. Clone this project:

   ```
   git clone https://github.com/sava-anti-ddos/topo.git
   ```
   Then:
   
   ```
   cd topo
   ```

2. Install the required tools and packages follow the [Requirements](#requirements) section.

   Or, use make:
   
   ```
   sudo make deps
   ``` 
   **!** Using make still need follow the [Requirements](#requirements) section to config dnsmasq.

3. Run the net by:

    ```
    sudo python3 main.py
    ```
    or use make:
    ```
    sudo make run
    ```
    After the net is started, you can use the mininet CLI to check the network status. `pingall` command will success after serval minutes.

4. After all nodes are connected, run the dns reflection attack simulation:

    First, run the victim side traffic audit at h5 using:
    ```
    sudo python3 dns_response_audit.py
    ```
    or
    ```
    sudo make audit
    ```
    
    Then, run the attack simulation at h2 using:
    ```
    sudo python3 dns_query_attack.py
    ```
    or
    ```
    sudo make attack
    ```
    After the attack is ended and the audit is finished, use `ctrl+c` to stop the audit process. The audit result will be saved to `audit/audit_traffic.csv`.

    Finally, run the visualization:
    ```
    sudo python3 attack_visualization.py
    ```
    or 
    ```
    sudo make visu
    ```
    The visualization will show the attack traffic and the background traffic. The result will be saved to `audit/attack_visualization.png`.

5. Exit the net in the mininet CLI by:

    ```
    exit
    ```
    You can use `sudo make clean_audit` to clean the audit result files and `sudo make clean` to clean the project.