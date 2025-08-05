# === wifi_monitor_llm_agent.py ===

import scapy.all as scapy
import subprocess
import socket
import requests
import time
import json
import functools
import sys
import os

from llm_prompts import generate_device_description_cached

# Optional: use Hugging Face API or local model like ollama
LLM_API_URL = "http://localhost:11434/api/generate"  # Ollama default endpoint
# MODEL_NAME = "phi3"  # or 
# MODEL_NAME = "mistral" # or
MODEL_NAME = "llama3" 

sys.path.append('..')

@functools.lru_cache(maxsize=256)
def get_mac_vendor(mac):
    try:
        # Use your existing utils
        from event_detection.utils import get_product_name_by_mac
        return get_product_name_by_mac(mac)
    except:
        return "Unknown"

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"

def scan_network(interface="wlan0"):
    print("[+] Scanning network ARP table...")
    arp_request = scapy.ARP(pdst="192.168.1.0/24")
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered = scapy.srp(arp_request_broadcast, timeout=2, verbose=0)[0]
    devices = []
    for element in answered:
        ip = element[1].psrc
        mac = element[1].hwsrc
        oui = mac[:8].upper()  # Get the first 8 characters of MAC for OUI
        hostname = get_hostname(ip)
        vendor = get_mac_vendor(mac)
        devices.append({"ip": ip, "mac": mac, "oui": oui, "hostname": hostname, "vendor": vendor})
    return devices


def generate_device_description(device):
    return generate_device_description_cached(
        device['mac'], device['ip'], device['hostname'], 
        device['vendor'], device['oui']
    )

def main():
    while True:
        devices = scan_network()
        
        if devices:
            print("\nDetected Devices:")
            print("| IP           | Hostname      | Vendor | Description                           |")
            print("| ------------ | ------------- | ------ | ------------------------------------- |")
            
            for device in devices:
                description = generate_device_description(device)
                # Clean up the description to fit in table format (max ~1000 chars for readability)
                description_short = description.replace('\n', ' ').strip()
                if len(description_short) > 1000:
                    description_short = description_short[:1000] + "..."
                
                # Format each field to fit table columns
                ip = device['ip'].ljust(12)
                hostname = device['hostname'][:12].ljust(13)  # Truncate if too long
                vendor = device['vendor'][:8].ljust(6)        # Truncate if too long
                
                print(f"| {ip} | {hostname} | {vendor} | {description_short.ljust(37)} |")
        else:
            print("\nNo devices detected.")
            
        print("\nSleeping 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
