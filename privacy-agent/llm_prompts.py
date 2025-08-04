import functools
import requests

# Optional: use Hugging Face API or local model like ollama
LLM_API_URL = "http://localhost:11434/api/generate"  # Ollama default endpoint
# MODEL_NAME = "phi3"  # or 
# MODEL_NAME = "mistral" # or
MODEL_NAME = "llama3" 


@functools.lru_cache(maxsize=256)
def generate_device_description_cached(mac, ip, hostname, vendor, oui):
    device = {"ip": ip, "mac": mac, "oui": oui, "hostname": hostname, "vendor": vendor}
    prompt = f"""
    You are a network device analyzer. Based on device information, 
    provide a brief description of what the device likely is and its common use.

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
    Describe this device in 1 sentence in the same format of the given examples. 
    Remove the "Device Info" and "Description" labels, just provide the description."""

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