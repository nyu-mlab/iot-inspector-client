"""
Sends out ARP spoofing packets for devices in the Device table.

"""
import time
import scapy.all as sc
import core.global_state as global_state
import core.common as common
import core.networking as networking
import core.config as config
import core.model as model
import traceback

# How many seconds between successive ARP spoofing attempts for each host
INTERNET_SPOOFING_INTERVAL = 2


spoof_stat_dict = {
    'last_internet_spoof_ts': 0
}


def spoof_internet_traffic():
    """
    Sends out ARP spoofing packets between inspected devices and the gateway.

    """
    if not global_state.is_inspecting:
        return

    # Check the consent
    if not config.get('has_consented_to_overall_risks', False):
        return

    # Check if enough time has passed since the last time we spoofed internet traffic
    if time.time() - spoof_stat_dict['last_internet_spoof_ts'] < INTERNET_SPOOFING_INTERVAL:
        return

    # Get all inspected devices
    inspected_device_list = []
    criteria = (model.Device.is_inspected == 1) & (model.Device.ip_addr != '')
    with model.db:
        for device in model.Device.select().where(criteria):
            inspected_device_list.append(device)

    # Get the gateway's IP and MAC addresses
    gateway_ip_addr = global_state.gateway_ip_addr
    try:
        gateway_mac_addr = global_state.arp_cache.get_mac_addr(gateway_ip_addr)
    except KeyError:
        common.log(f'Gateway (ip: {gateway_ip_addr}) MAC address not found in ARP cache. Cannot spoof internet traffic yet.')
        return

    common.log(f'[ARP Spoofer] Spoofing internet traffic for {len(inspected_device_list)} devices')

    # Send ARP spoofing packets for each inspected device
    for device in inspected_device_list:
        # Make sure that the device is in the ARP cache; if not, skip
        try:
            global_state.arp_cache.get_ip_addr(device.mac_addr)
        except KeyError:
            continue
        try:
            send_spoofed_arp(device.mac_addr, device.ip_addr, gateway_mac_addr, gateway_ip_addr)
        except Exception:
            common.log(f'[ARP Spoofer] Error spoofing {device.mac_addr}, {device.ip_addr} <-> {gateway_mac_addr}, {gateway_ip_addr}, because\n' + traceback.format_exc())

    spoof_stat_dict['last_internet_spoof_ts'] = time.time()



def send_spoofed_arp(victim_mac_addr, victim_ip_addr, dest_mac_addr, dest_ip_addr):
    """
    Sends out bidirectional ARP spoofing packets to the victim so that the host running Inspector appears to have the `dest_ip_addr` IP address.

    """
    host_mac_addr = global_state.host_mac_addr

    if victim_ip_addr == dest_ip_addr:
        return

    # Do not spoof packets if we're not globally inspecting
    with global_state.global_state_lock:
        if not global_state.is_inspecting:
            return

    # Send ARP spoof request to destination, so that the destination host thinks that Inspector's host is the victim.

    dest_arp = sc.ARP()
    dest_arp.op = 1
    dest_arp.psrc = victim_ip_addr
    dest_arp.hwsrc = host_mac_addr
    dest_arp.pdst = dest_ip_addr
    dest_arp.hwdst = dest_mac_addr

    sc.send(dest_arp, iface=global_state.host_active_interface, verbose=0)

    # Send ARP spoof request to victim, so that the victim thinks that Inspector's host is the destination.

    victim_arp = sc.ARP()
    victim_arp.op = 1
    victim_arp.psrc = dest_ip_addr
    victim_arp.hwsrc = host_mac_addr
    victim_arp.pdst = victim_ip_addr
    victim_arp.hwdst = victim_mac_addr

    sc.send(victim_arp, iface=global_state.host_active_interface, verbose=0)



def reset_arp_tables():
    pass