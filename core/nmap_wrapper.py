import nmap
import json
import time

import core.model as model
import core.common as common
import core.global_state as global_state
import core.config as config

NMAP_SCAN_INTERVAL = 300

# {mac1-port1:scan_time1, mac1-port2:scan_time2} 
last_scan_time_record = {}

def scan(ip_port_list, arguments = "-sV --script vuln", timeout = 180):
    """ Execute scan on given ip_port_list """

    scanner = nmap.PortScanner()

    # Restruct target by ip
    target_ports_by_ip = {}
    for entry in ip_port_list:
        ip, port = entry
        if ip in target_ports_by_ip:
            target_ports_by_ip[ip].append(port)
        else:
            target_ports_by_ip[ip] = [port]

    target_ips = target_ports_by_ip.keys()
    results_by_ip = {}

    # Launch scan on each ip
    for ip in target_ips:
        common.log(f"[Nmap Scan] Start Scan {ip}:{target_ports_by_ip[ip]}, timeout = {timeout}")

        # Launch scan for this ip
        ports_str = ",".join(str(port) for port in target_ports_by_ip[ip])
        # It will block until finish
        scanner.scan(hosts = ip, ports = ports_str, arguments = arguments)

        # Save result of this ip
        result_for_this_ip = {}
        # If this device is down
        if ip not in scanner.all_hosts():
            common.log(f"[Nmap Scan] {ip} Device Down")
            for port in target_ports_by_ip[ip]:
                result_for_this_ip[port] = "Device Down"
        else:
            for port in target_ports_by_ip[ip]:
                result_for_this_ip[port] = scanner[ip]['tcp'][port]
                common.log(f"[Nmap Scan] {ip}:{port} Results: {result_for_this_ip[port]}")

        results_by_ip[ip] = result_for_this_ip

    # store results respect to the order in ip_port_list
    results = []
    for entry in ip_port_list:
        ip, port = entry
        results.append(results_by_ip[ip][port])

    return results

# The rests are similar to banner_grab

def get_current_devices():
    """Get known valid devices. Same as that one in banner_grab"""

    target_device_list = []
    criteria = (model.Device.is_inspected == 1) & (model.Device.ip_addr != '')

    with model.db:
        for device in model.Device.select().where(criteria):
            target_device_list.append(device)

    return target_device_list

def build_ip_port_list(device, target_port_list):
    """ Build target ip:port list for a given device """

    target_ip_port_list = []

    with model.db:
        ip = device.ip_addr

    if target_port_list == None:

        with model.db:
            ports = json.loads(device.open_tcp_ports)
            for port in ports:

                if (device.mac_addr+"-"+str(port)) in last_scan_time_record:
                    if time.time() - last_scan_time_record[(device.mac_addr+"-"+str(port))] < NMAP_SCAN_INTERVAL:
                        common.log(f"[Nmap Scan] Give up too frequent scan {device.mac_addr} {ip}:{str(port)}")
                        continue

                target_ip_port_list.append((ip, port))
                common.log(f"[Nmap Scan] Set target port {device.mac_addr} {ip}:{str(port)}")
                last_scan_time_record[(device.mac_addr+"-"+str(port))] = time.time()
    else:
        for port in target_port_list:
            target_ip_port_list.append((ip, port))
            last_scan_time_record[(device.mac_addr+"-"+str(port))] = time.time()

    return target_ip_port_list


def store_result_to_database(device, target_ip_port_list, result):

    # Build result Dict.
    result_dict = {}
    for i in range(0, len(target_ip_port_list)):
        ip, port = target_ip_port_list[i]
        result_dict[port] = result[i]

    # Store to DB (simply use dict.update)
    with model.write_lock:
        with model.db:

            known_port_nmap_results = json.loads(device.port_nmap_results)
            common.log(f"[Nmap Scan] From database get IP:{device.ip_addr} Known Nmap Results:{known_port_nmap_results}")

            known_port_nmap_results.update(result_dict)
            device.port_nmap_results = json.dumps(known_port_nmap_results)

            device.save()
            common.log(f"[Nmap Scan] Store to database IP:{device.ip_addr} Nmap Results:{device.port_nmap_results}")



def run_nmap_scan(target_device_list = None, target_ports_list = None, arguments = "-sV --script vuln", timeout = 180):

    if not global_state.is_inspecting:
        return

    # Check the consent
    if not config.get('has_consented_to_overall_risks', False):
        return

    # target_ports_list is List[List], each list for each device
    # port_list and device_list must be one-to-one relation
    if target_ports_list != None:
        if (target_device_list == None) or (len(target_device_list) != len(target_ports_list)):
            common.log("[Nmap Scan] Args not qualified!")
            return

    # Define target devices to scan
    if target_device_list == None:
        target_device_list = get_current_devices()

    if len(target_device_list) == 0:
        common.log("[Nmap Scan] No valid target device to scan")
        return


    # Run Nmap scan on each device one by one
    for i in range(0, len(target_device_list)):
        device = target_device_list[i]

        # Make sure that the device is in the ARP cache; if not, skip
        try:
            global_state.arp_cache.get_ip_addr(device.mac_addr)
        except KeyError:
            continue

        # Build target ip_port list
        if target_ports_list == None:
            target_ip_port_list = build_ip_port_list(device, None)
        else:
            target_ip_port_list = build_ip_port_list(device, target_ports_list[i])

        if len(target_ip_port_list) == 0:
            common.log(f"[Nmap Scan] No target ports to scan for {device.mac_addr} {device.ip_addr}")


        # Run the Nmap Scan
        result = scan(target_ip_port_list, arguments, timeout)

        # Store the result of this device to database
        if len(result) > 0:
            store_result_to_database(device, target_ip_port_list, result)

    common.log("[Nmap Scan] Exit nmap scan")