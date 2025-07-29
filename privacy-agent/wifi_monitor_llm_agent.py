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


@functools.lru_cache(maxsize=256)
def generate_device_description_cached(mac, ip, hostname, vendor, oui):
    device = {"ip": ip, "mac": mac, "oui": oui, "hostname": hostname, "vendor": vendor}
    prompt = f"""
You are a network device analyzer. Based on device information, provide a brief description of what the device likely is and its common use.

Examples:
Device Info:
- IP: 192.168.1.24
- MAC: aa:bb:cc:dd:ee:ff
- OUI: AA:BB:CC
- Hostname: android-dcbab
- Vendor: Google
Description: Android phone streaming social apps

Device Info:
- IP: 192.168.1.5
- MAC: 11:22:33:44:55:66
- OUI: 11:22:33
- Hostname: LGWebOSTV
- Vendor: LG
Description: LG smart TV likely used for Netflix

Device Info:
- IP: 192.168.1.10
- MAC: ff:ee:dd:cc:bb:aa
- OUI: FF:EE:DD
- Hostname: hp-printer
- Vendor: HP
Description: Wireless printer connected over Wi-Fi

Now analyze this device:
Device Info:
- IP: {device['ip']}
- MAC: {device['mac']}
- OUI: {device['oui']}
- Hostname: {device['hostname']}
- Vendor: {device['vendor']}
Describe this device in 1 sentence in the same format of the given examples. Remove the "Device Info" and "Description" labels, just provide the description."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(LLM_API_URL, json=payload)
        return response.json().get("response", "No response").strip()
    except Exception as e:
        return f"LLM error: {str(e)}"

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
