# This is a makefile for building and managing topo project.

# Variables
SHELL		= /bin/bash
HOME 		= $(shell echo $$HOME)

default: help

# Target: all
# Description: Build the entire project.
all:
	@echo "Building the project..."

# Target: clean
# Description: Clean the project by removing all generated files.
clean:
	@echo "Cleaning the project..."
	@rm -rf __pycache__
	@rm -rf audit
	@rm -rf conf/**/*.log
	@rm -rf conf/**/*.pid
	@rm -rf conf/**/*.api
	@rm -rf log
	@echo "Removing h4-eth0 interface..."
	@sudo ip link delete h4-eth0
	@echo "Removing routes added by h4..."
	@sudo ip route del 20.20.0.0/16 via 30.30.10.1
	@sudo ip route del 30.30.0.0/16 via 30.30.10.1
	@sudo ip route del 40.40.0.0/16 via 30.30.10.1
	@sudo ip route del 50.50.0.0/16 via 30.30.10.1

# Target: run
# Description: Run the project.
run:
	@echo "Running the project..."
	@echo "Needs root privileges to run the project"
	sudo python3 main.py
	

# Target: install
# Description: Install the project.
install:
	@echo "Installing the project..."

help:
	@echo "make deps		install dependencies"
	@echo "make help		display this help message"
	@echo "make run		run the project"
	@echo "make visu		visualize the attack"
	@echo "make attack		launch DNS reflection attack(run at h2)"
	@echo "make audit		audit DNS reflection attack(run at h5)"
	@echo "make clean		clean the project"

visu:
	@echo "Visualizing the attack..."
	@echo "Needs root privileges to run"
	sudo python3 attack_visualization.py

attack:
	@echo "Launching DNS reflection attack...(run this at h2)"
	@echo "Needs root privileges to run"
	sudo python3 dns_query_attack.py

audit:
	@echo "Auditing DNS reflection attack...(run this at h5)"
	@echo "Needs root privileges to run"
	sudo python3 dns_response_audit.py

deps:
	@echo "Installing dependencies..."
	@echo "Needs root privileges to install dependencies"
	
# install python3
	@echo -e "\033[32mInstalling python3 enviornment\033[0m"
	sudo apt install python3 python-is-python3 python3-pip -y

# install python packages
	@echo -e "\033[32mInstalling python packages\033[0m"
	sudo pip3 install -r requirements.txt

# install mininet
	@echo -e "\033[32mInstalling mininet enviornment\033[0m"
	sudo apt install mininet -y

# install quagga
	@echo -e "\033[32mInstalling quagga enviornment\033[0m"
	sudo apt install quagga -y

# install dnsmasq
	@echo -e "\033[32mInstalling dnsmasq enviornment\033[0m"
	sudo apt install dnsmasq -y

# install xterm
	@echo -e "\033[32mInstalling xterm enviornment\033[0m"
	sudo apt install xterm -y

clean_deps:
	@echo "Cleaning dependencies..."
	@echo "Needs root privileges to clean dependencies"
	
# remove python3
	@echo -e "\033[32mRemoving python3 enviornment\033[0m"
	sudo apt remove python3 python-is-python3 python3-pip -y

# remove python packages
	@echo -e "\033[32mRemoving python packages\033[0m"
	sudo pip3 uninstall -r requirements.txt

# remove mininet
	@echo -e "\033[32mRemoving mininet enviornment\033[0m"
	sudo apt remove mininet -y

# remove quagga
	@echo -e "\033[32mRemoving quagga enviornment\033[0m"
	sudo apt remove quagga -y

# remove dnsmasq
	@echo -e "\033[32mRemoving dnsmasq enviornment\033[0m"
	sudo apt remove dnsmasq -y

# remove xterm
	@echo -e "\033[32mRemoving xterm enviornment\033[0m"
	sudo apt remove xterm -y