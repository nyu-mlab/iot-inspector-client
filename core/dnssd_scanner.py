# some codes come from https://paper.seebug.org/1727/#0x02-dns-sd

import socket
from scapy.all import raw, DNS, DNSQR
import time
import json

import core.model as model
import core.common as common
import core.global_state as global_state
import core.config as config

TIME_OUT = 5
DNSSD_SCAN_INTERVAL = 120

# {mac1:scan_time1, mac2:scan_time2}
last_scan_time_record = {}

def try_best_decode(data):
    if isinstance(data, bytes):
        return data.decode('utf-8')
    if isinstance(data, list):
        new_list = [item.decode('utf-8') for item in data]
        return new_list
    return data

def get_service_info(sock, target_ip, service):
    """ Query a single service for detailed info"""

    # return: list[{"rrname":, "target":, "rdata":}]
    sub_services = []

    req = DNS(id=0x0001, rd=1, qd=DNSQR(qtype="PTR", qname=service))
    try:
        sock.sendto(raw(req), (target_ip, 5353))
        data, _ = sock.recvfrom(1024)
        resp = DNS(data)
    except:
        return sub_services

    try:
        for i in range(0, resp.arcount):
            this_sub_service = {"rrname":"", "target":"", "rdata":""}

            this_sub_service["rrname"] = try_best_decode(resp.ar[i].rrname)
            if hasattr(resp.ar[i], "port"):
                this_sub_service["rrname"] += (" " + str(resp.ar[i].port))

            if hasattr(resp.ar[i], "target"):
                this_sub_service["target"] = try_best_decode(resp.ar[i].target)

            if hasattr(resp.ar[i], "rdata"):
                this_sub_service["rdata"] = try_best_decode(resp.ar[i].rdata)

            sub_services.append(this_sub_service)
            common.log(f"[DNS-SD Scan] service:{service} get sub services:{this_sub_service}")
    except:
        common.log(f"[DNS-SD Scan] Error Decoding")

    return sub_services


def scan(target_ip_list):
    """ Launch DNS-SD Scan """

    common.log('[DNS-SD Scan] Start')
    common.log('[DNS-SD Scan] Scanning %d locations: %s' % (len(target_ip_list), target_ip_list))

    result_list = []

    for i in range(0, len(target_ip_list)):
        target_ip = target_ip_list[i]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(TIME_OUT)

        # query all service names
        req = DNS(id=0x0001, rd=1, qd=DNSQR(qtype="PTR", qname="_services._dns-sd._udp.local"))

        try:
            sock.sendto(raw(req), (target_ip, 5353))
            data, _ = sock.recvfrom(1024)
            resp = DNS(data)
            common.log("[DNS-SD Scan] No.%d %s ONLINE" % (i, target_ip))

            services = []
            for i in range(0, resp.ancount):
                service = (resp.an[i].rdata).decode()
                this_sub_services = get_service_info(sock, target_ip, service)
                services.append({service : this_sub_services})

            result_list.append({"ip":target_ip, "scan_time":time.time(), "status":"ONLINE", "services":services})

        except:
            common.log("[DNS-SD Scan] No.%d %s OFFLINE" % (i, target_ip))
            result_list.append({"ip":target_ip, "scan_time":time.time(), "status":"OFFLINE", "services":[]})

    common.log('[DNS-SD Scan] Finish')
    return result_list


def get_current_devices():
    """ Get known valid devices """

    target_device_list = []
    criteria = (model.Device.is_inspected == 1) & (model.Device.ip_addr != '')

    with model.db:
        for device in model.Device.select().where(criteria):
            target_device_list.append(device)

    return target_device_list


def filter_frequent_scan_devices(current_devices):
    """ Remove devices that has been scanned recently and set new scan time reocrd """

    target_device_list = []

    for device in current_devices:
        if device.mac_addr in last_scan_time_record:
            if time.time() - last_scan_time_record[device.mac_addr] < DNSSD_SCAN_INTERVAL:
                continue
        last_scan_time_record[device.mac_addr] = time.time()
        target_device_list.append(device)

    return target_device_list


def store_result_to_database(device, result):
    """ Store DNS-SD scan result for one device """

    with model.write_lock:
        with model.db:
            model_instance = model.mDNSInfoModel.get_or_none(mac=device.mac_addr)
            common.log(f"[DNS-SD Scan] {result['services']}")
            # Create a new entry
            if model_instance is None:
                model.mDNSInfoModel.create(
                    mac = device.mac_addr,
                    ip = result['ip'],
                    scan_time = result['scan_time'],
                    status = result['status'],
                    services = json.dumps(result['services'])
                )
                common.log(f"[DNS-SD Scan] Create new mDNS info for {device.mac_addr} {result['ip']}")

            else:
                if model_instance.status == "ONLINE" and result['status'] == "OFFLINE":
                    common.log(f"[DNS-SD Scan] Give up update info for {device.mac_addr} {result['ip']}")
                    return
                model_instance.ip = result['ip']
                model_instance.scan_time = result['scan_time']
                model_instance.status = result['status']
                model_instance.services = json.dumps(result['services'])
                model_instance.save()
                common.log(f"[DNS-SD Scan] Update info for {device.mac_addr} {result['ip']}")


def run_dnssd_scan(target_device_list = None):
    """ Main API for Scan mDNS services on devices we have found """

    if not global_state.is_inspecting:
        return

    # Check the consent
    if not config.get('has_consented_to_overall_risks', False):
        return

    # Define target deivce to scan
    if target_device_list == None:
        current_devices = get_current_devices()
        target_device_list = filter_frequent_scan_devices(current_devices)

    if len(target_device_list) == 0:
        common.log("[DNS-SD Scan] No valid target device to scan")
        return

    # Run DNS-SD scan on each device one by one
    for device in target_device_list:

        # Make sure that the device is in the ARP cache; if not, skip
        try:
            global_state.arp_cache.get_ip_addr(device.mac_addr)
        except KeyError:
            continue

        # Run the scan for each target
        results = scan([device.ip_addr])

        # Save data to DB immediately after one scan is finished
        # Since only one IP is given to scan(), we fetch the first and the only result
        this_result = results[0]
        store_result_to_database(device, this_result)

    # Exit
    common.log(f"[DNS-SD Scan] Exit DNS-SD scan")