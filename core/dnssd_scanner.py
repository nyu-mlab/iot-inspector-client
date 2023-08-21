# some codes come from https://paper.seebug.org/1727/#0x02-dns-sd

import socket
import sys
from scapy.all import raw, DNS, DNSQR
import time
import xml.etree.ElementTree as ET

import core.model as model
import core.common as common
import core.global_state as global_state
import core.config as config

class DNSSDScanner():

    def __init__(self):
        self.result_collect = []

    def get_service_info(self, sock, target_ip, service):
        

        # query each service detail informations
        req = DNS(id=0x0001, rd=1, qd=DNSQR(qtype="PTR", qname=service))
        #req.show()

        try:
            sock.sendto(raw(req), (target_ip, 5353))
            data, _ = sock.recvfrom(1024)
            resp = DNS(data)
        except:
            return []
        #resp.show()

        # parse additional records
        repeat = {}
        services = []
        for i in range(0, resp.arcount):
            rrname = (resp.ar[i].rrname).decode()
            rdata  = resp.ar[i].rdata

            if rrname in repeat:
                continue
            repeat[rrname] = rdata

            if hasattr(resp.ar[i], "port"):
                rrname += (" " + str(resp.ar[i].port))

            if rrname.find("._device-info._tcp.local.") > 0:
                print(" "*4, rrname, rdata)
            else:
                print(" "*4, rrname)
            services.append(rrname)

        return services
    # end get_service_info()

    # no concurrent operations here
    def scan(self, target_ip_list): # we don't need to specify port here, because we know mDNS uses 5353

        print('[DNS-SD Scan] Start')
        print('[DNS-SD Scan] Scanning %d locations: %s' % (len(target_ip_list), target_ip_list))
        common.log('[DNS-SD Scan] Start')
        common.log('[DNS-SD Scan] Scanning %d locations: %s' % (len(target_ip_list), target_ip_list))

        for i in range(0, len(target_ip_list)):
            target_ip = target_ip_list[i]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)

            # query all service name
            req = DNS(id=0x0001, rd=1, qd=DNSQR(qtype="PTR", qname="_services._dns-sd._udp.local")) 
            #req.show()

            try:
                sock.sendto(raw(req), (target_ip, 5353))
                data, _ = sock.recvfrom(1024)

                resp = DNS(data)
                #resp.show()

                print("[DNS-SD Scan] No.%d %s ONLINE" % (i, target_ip))
                common.log("[DNS-SD Scan] No.%d %s ONLINE" % (i, target_ip))

                services = []
                for i in range(0, resp.ancount):
                    service = (resp.an[i].rdata).decode()
                    this_services = self.get_service_info(sock, target_ip, service)
                    services.append(this_services)
                self.result_collect.append({"ip":target_ip, "scan_time":time.time(), "status":"ONLINE", "services":services})


            except KeyboardInterrupt:
                exit(0)
            except:
                print("[DNS-SD Scan] No.%d %s OFFLINE" % (i, target_ip))
                common.log("[DNS-SD Scan] No.%d %s OFFLINE" % (i, target_ip))
                self.result_collect.append({"ip":target_ip, "scan_time":time.time(), "status":"OFFLINE", "services":[]})

        print('[DNS-SD Scan] Finish')
        common.log('[DNS-SD Scan] Finish')

    # end dnssd_scan()

    def getResult(self):
        return self.result_collect
    
    def clearResult(self):
        self.result_collect = []


DNSSD_SCAN_INTERVAL = 60
scan_status_record = {} # {mac1:scan_time1, mac2:scan_time2}


def run_dnssd_scan():
    """
    Scan for mDNS services on devices we have found

    """

    if not global_state.is_inspecting:
        return

    # Check the consent
    if not config.get('has_consented_to_overall_risks', False):
        return

    # Get all inspected devices
    inspected_device_list = []
    criteria = (model.Device.is_inspected == 1) & (model.Device.ip_addr != '')
    with model.db:
        for device in model.Device.select().where(criteria):
            if device.mac_addr in scan_status_record:
                if time.time() - scan_status_record[device.mac_addr] < DNSSD_SCAN_INTERVAL:
                    continue
            inspected_device_list.append(device)

    DNSSDScannerInstance = DNSSDScanner()

    for device in inspected_device_list:  # imitate what's in arp sproof to get latest IPs

        # Make sure that the device is in the ARP cache; if not, skip
        try:
            global_state.arp_cache.get_ip_addr(device.mac_addr)
        except KeyError:
            continue
        
        # run the scan for each target
        DNSSDScannerInstance.scan([device.ip_addr])
        scan_status_record[device.mac_addr] = time.time()
        
        # save data to DB immediately after one scan is finished
        results = DNSSDScannerInstance.getResult()
        for result in results:

            with model.write_lock:
                with model.db:

                    model_instance = model.mDNSInfoModel.get_or_none(mac=device.mac_addr)

                    if model_instance is None:
                        model.mDNSInfoModel.create(
                            mac = device.mac_addr,
                            ip = result['ip'],
                            scan_time = result['scan_time'],
                            status = result['status'],
                            services = result['services']
                        )

                    else: # risk: may wipe out useful infomation when a device become offline
                        if eval(model_instance.services) != result['services']:
                            model_instance.ip = result['ip']
                            model_instance.scan_time = result['scan_time']
                            model_instance.status = result['status']
                            model_instance.services = result['services']
                            model_instance.save()

        DNSSDScannerInstance.clearResult()

    # exit
    del DNSSDScannerInstance
