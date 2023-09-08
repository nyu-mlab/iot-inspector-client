# some codes come from https://github.com/tenable/upnp_info and https://paper.seebug.org/1727/#0x03-ssdp

import re
import sys
import time
import base64
import struct
import socket
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import core.model as model
import core.common as common
import core.global_state as global_state
import core.config as config

class SSDPInfo():

    def __init__(self):

        self.scan_time = 0

        self.location = ""
        self.ip = ""
        self.port = ""
        self.outer_file_name = ""
        self.original_reply = ""

        self.server_string = ""
        self.device_type = ""
        self.friendly_name = ""
        self.manufacturer = ""
        self.manufacturer_url = ""
        self.model_description = ""
        self.model_name = ""
        self.model_number = ""

        self.services_list = []


class SSDPScanner():

    def __init__(self):
        self.result_collect = []

    ###
    # Send a multicast message tell all the pnp services that we are looking
    # For them. Keep listening for responses until we hit a 3 second timeout (yes,
    # this could technically cause an infinite loop). Parse the URL out of the
    # 'location' field in the HTTP header and store for later analysis.
    #
    # @return the set of advertised upnp locations, and IPs
    ###
    def discover_pnp_locations(self):
        common.log('[SSDP Scan] Discovering UPnP locations')
        locations = []
        ip_ports = []
        original_replys = []
        location_regex = re.compile("location:[ ]*(.+)\r\n", re.IGNORECASE)
        ip_port_regex = r"http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)"
        ssdpDiscover = ('M-SEARCH * HTTP/1.1\r\n' +
                        'HOST: 239.255.255.250:1900\r\n' +
                        'MAN: "ssdp:discover"\r\n' +
                        'MX: 1\r\n' +
                        'ST: ssdp:all\r\n' +
                        '\r\n')

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sock.setblocking(False) # we are not async here, so we don't make it nonblocking
        sock.sendto(ssdpDiscover.encode('ASCII'), ("239.255.255.250", 1900))
        sock.settimeout(5)
        try:
            while True:
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                location_result = location_regex.search(data.decode('ASCII'))
                if location_result and (location_result.group(1) in locations) == False:
                    locations.append(location_result.group(1))
                    match = re.search(ip_port_regex, location_result.group(1))
                    ip = match.group(1)
                    port = match.group(2)
                    ip_port = ip + "_" + port
                    ip_ports.append(ip_port)
                    original_replys.append(data.decode('ASCII'))

        except socket.error:
            sock.close() # Exit while loop with exception, so this line will always been executed

        common.log('[SSDP Scan] %d locations found:' % len(locations))
        for location in locations:
            common.log('[SSDP Scan]\t%s' % location)
        return locations, ip_ports, original_replys

    ##
    # Tries to print an element extracted from the XML.
    # @param xml the xml tree we are working on
    # @param xml_name the name of the node we want to pull text from
    # @param print_name the name we want to appear in stdout
    ##
    def print_attribute(self, xml, xml_name, print_name):
        try:
            temp = xml.find(xml_name).text
            common.log('\t-> %s: %s' % (print_name, temp))
            return temp
        except AttributeError:
            return None

    ###
    # Loads the XML at each location and prints out the API along with some other
    # interesting data.
    #
    # @param locations a collection of URLs
    # @return igd_ctr (the control address) and igd_service (the service type)
    ###
    def parse_locations(self, locations, original_replys):
        if len(locations) < 1:
            common.log('[SSDP Scan] No location to parse')
            return
        if len(locations) > 0:
            common.log('[SSDP Scan] Start parse %d locations:' % len(locations))

            for i in range(0, len(locations)):
                location = locations[i]
                original_reply = original_replys[i]

                if self.alreadyKnownThisLocation(location) == True:
                    common.log('[SSDP Scan] Already known %s' % location)
                    continue

                common.log('[SSDP Scan] Loading %s...' % location)
                ssdp_info = SSDPInfo()

                ssdp_info.original_reply = original_reply
                ssdp_info.scan_time = time.time()
                ssdp_info.location = location

                # DH: If there's no match, match will be `None` and the subsequent lines will throw an error
                match = re.search(r"http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)/(.*)", location)
                ssdp_info.ip = match.group(1)
                ssdp_info.port = match.group(2)
                ssdp_info.outer_file_name = match.group(3)

                try:
                    resp = requests.get(location, timeout=3)

                    # if we can reach this place, we must have got some reply
                    if resp.headers.get('server'):
                        server_string = resp.headers.get('server')
                        common.log('[SSDP Scan] \t-> Server String: %s' % server_string)
                        ssdp_info.server_string = server_string
                    else:
                        common.log('[SSDP Scan] \t-> No server string')

                    parsed = urlparse(location)

                    common.log('[SSDP Scan]\t==== XML Attributes ===')
                    try:
                        xmlRoot = ET.fromstring(resp.text)
                    except:
                        common.log('\t[SSDP Scan] Failed XML parsing of %s' % location)
                        continue

                    ssdp_info.device_type = self.print_attribute(xmlRoot, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}deviceType", "Device Type")
                    ssdp_info.device_type = self.print_attribute(xmlRoot, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}friendlyName", "Friendly Name")
                    ssdp_info.manufacturer = self.print_attribute(xmlRoot, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}manufacturer", "Manufacturer")
                    ssdp_info.manufacturer_url = self.print_attribute(xmlRoot, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}manufacturerURL", "Manufacturer URL")
                    ssdp_info.model_description = self.print_attribute(xmlRoot, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelDescription", "Model Description")
                    ssdp_info.model_name = self.print_attribute(xmlRoot, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelName", "Model Name")
                    ssdp_info.model_number = self.print_attribute(xmlRoot, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelNumber", "Model Number")

                    common.log('[SSDP Scan]\t-> Services:')
                    services = xmlRoot.findall(".//*{urn:schemas-upnp-org:device-1-0}serviceList/")
                    for service in services:
                        service_type = service.find('./{urn:schemas-upnp-org:device-1-0}serviceType').text
                        control = service.find('./{urn:schemas-upnp-org:device-1-0}controlURL').text
                        events = service.find('./{urn:schemas-upnp-org:device-1-0}eventSubURL').text
                        common.log('[SSDP Scan]\t\t=> Service Type: %s' % service_type)
                        common.log('[SSDP Scan]\t\t=> Control: %s' % control)
                        common.log('[SSDP Scan]\t\t=> Events: %s' % events)

                        this_service = {"service_url":"", "service_type":service_type, "control":control, "events":events, "actions":[]}

                        # Add a lead in '/' if it doesn't exist
                        scp = service.find('./{urn:schemas-upnp-org:device-1-0}SCPDURL').text
                        if scp[0] != '/':
                            scp = '/' + scp
                        serviceURL = parsed.scheme + "://" + parsed.netloc + scp
                        common.log('[SSDP Scan]\t\t=> API: %s' % serviceURL)

                        this_service['service_url'] = serviceURL

                        # read in the SCP XML
                        resp = requests.get(serviceURL, timeout=2)
                        try:
                            serviceXML = ET.fromstring(resp.text)
                        except:
                            common.log('[SSDP Scan]\t\t\t[!] Failed to parse the response XML')
                            continue

                        actions = serviceXML.findall(".//*{urn:schemas-upnp-org:service-1-0}action")
                        for action in actions:
                            action_name = action.find('./{urn:schemas-upnp-org:service-1-0}name').text
                            common.log(f'[SSDP Scan]\t\t\t- {action_name}')
                            this_service["actions"].append(action_name)

                        ssdp_info.services_list.append(this_service)

                except requests.exceptions.ConnectionError:
                    common.log('[SSDP Scan] Could not load %s' % location)
                except requests.exceptions.ReadTimeout:
                    common.log('[SSDP Scan] Timeout reading from %s' % location)

                self.result_collect.append(ssdp_info)
            common.log("[SSDP Scan] Done Parsing")
        return

    def scan(self):
        common.log("[SSDP Scan] Start.")
        locations, ip_ports, original_replys = self.discover_pnp_locations()
        self.parse_locations(locations, original_replys)
        common.log("[SSDP Scan] Finish.")

    def get_serv_ua(self, resp):
        lines = resp.split("\r\n")
        for i in lines:
            array = i.split(":")
            if array[0].upper() == "SERVER" or array[0].upper() == "USER-AGENT":
                return array[1]

    def alreadyKnownThisLocation(self, location):
        for known_location_info in self.result_collect:
            if known_location_info.location == location:
                return True
        return False

    # Don't use it for now.
    def sniff(self, sniff_time = 10): # Don't run it with scan() at the same time

        common.log(f"[SSDP Scan] [sniffer mode] Max sniff time = {str(sniff_time)}")
        common.log("[SSDP Scan] [sniffer mode] start")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)

        try:
            # ! can not work on windows here
            sock.bind(("239.255.255.250", 1900))
        except:
            common.log("[SSDP Scan] System does not support SSDP sniff")
            sock.close()
            return

        # join the multicast group
        maddr = struct.pack("4sl", socket.inet_aton("239.255.255.250"), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, maddr)

        # receive and print

        location_regex = re.compile("location:[ ]*(.+)\r\n", re.IGNORECASE)
        ip_port_regex = r"http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)"
        locations = []
        ip_ports = []
        original_replys = []

        start_time = time.time()

        continue_listen = True
        while continue_listen:
            try:
                resp, raddr = sock.recvfrom(1024)
                #data = self.get_serv_ua(resp.decode())
                #print("\n")
                #print("####RESP =", resp)
                #print("####raddr =", raddr)
                common.log(f"[SSDP Scan] [sniffer find], {raddr[0]}, {resp}")

                location_result = location_regex.search(resp.decode('ASCII'))
                if location_result and (location_result.group(1) in locations) == False:
                    locations.append(location_result.group(1))
                    match = re.search(ip_port_regex, location_result.group(1))
                    ip = match.group(1)
                    port = match.group(2)
                    ip_port = ip + "_" + port
                    ip_ports.append(ip_port)
                    original_replys.append(resp.decode('ASCII'))

                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time > sniff_time:
                    common.log("[SSDP Scan] time is up")
                    continue_listen = False

            except:
                common.log("[SSDP Scan] no msg in 5s")
                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time > sniff_time:
                    common.log("[SSDP Scan] time is up")
                    continue_listen = False


        sock.close()

        if len(locations) > 0:
            self.parse_locations(locations, original_replys)

        common.log("[SSDP Scan] [sniffer mode] exit")

    def getResult(self):
        return self.result_collect

    def clearResult(self):
        self.result_collect = []




def run_ssdp_scan():
    """
    Sends out SSDP requests to discover services

    """

    if not global_state.is_inspecting:
        return

    # Check the consent
    if not config.get('has_consented_to_overall_risks', False):
        return

    common.log("[SSDP Scan] Ready to start SSDP scan")

    # create scanner instance and run SSDP scan
    SSDPScannerInstance = SSDPScanner()
    SSDPScannerInstance.scan() # it will block until no more new device found in 5 seconds

    common.log("[SSDP Scan] Done SSDP scan, start restore data")

    # save data to DB
    current_results = SSDPScannerInstance.getResult()

    with model.write_lock:
        with model.db:

            for SSDPInfoInst in current_results:

                model_instance = model.SSDPInfoModel.get_or_none(ip=SSDPInfoInst.ip, port=SSDPInfoInst.port)

                if model_instance is None:

                    model.SSDPInfoModel.create(

                        mac = "unknown", # we will deal with it later

                        scan_time = SSDPInfoInst.scan_time,
                        location = SSDPInfoInst.location,
                        ip = SSDPInfoInst.ip,
                        port = SSDPInfoInst.port,
                        outer_file_name = SSDPInfoInst.outer_file_name,
                        original_reply = SSDPInfoInst.original_reply,

                        server_string = SSDPInfoInst.server_string,
                        device_type = SSDPInfoInst.device_type,
                        friendly_name = SSDPInfoInst.friendly_name,
                        manufacturer = SSDPInfoInst.manufacturer,
                        manufacturer_url = SSDPInfoInst.manufacturer_url,
                        model_description = SSDPInfoInst.model_description,
                        model_name = SSDPInfoInst.model_name,
                        model_number = SSDPInfoInst.model_number,

                        services_list = SSDPInfoInst.services_list
                    )

                    common.log(f"[SSDP Scan] Create new ssdp info for {SSDPInfoInst.ip}:{SSDPInfoInst.port}")

                else:
                    model_instance.scan_time = SSDPInfoInst.scan_time,
                    model_instance.location = SSDPInfoInst.location,
                    model_instance.ip = SSDPInfoInst.ip,
                    model_instance.port = SSDPInfoInst.port,
                    model_instance.outer_file_name = SSDPInfoInst.outer_file_name,
                    model_instance.original_reply = SSDPInfoInst.original_reply,

                    model_instance.server_string = SSDPInfoInst.server_string,
                    model_instance.device_type = SSDPInfoInst.device_type,
                    model_instance.friendly_name = SSDPInfoInst.friendly_name,
                    model_instance.manufacturer = SSDPInfoInst.manufacturer,
                    model_instance.manufacturer_url = SSDPInfoInst.manufacturer_url,
                    model_instance.model_description = SSDPInfoInst.model_description,
                    model_instance.model_name = SSDPInfoInst.model_name,
                    model_instance.model_number = SSDPInfoInst.model_number,

                    model_instance.services_list = SSDPInfoInst.services_list

                    model_instance.save()

                    common.log(f"[SSDP Scan] Update ssdp info for {SSDPInfoInst.ip}:{SSDPInfoInst.port}")

            # using global_state.arp_cache to bind ip to mac.
            # also update for those found in previous rounds except for those scanned in more than 5 mins ago
            for model_instance in model.SSDPInfoModel.select().where(model.SSDPInfoModel.mac == "unknown"):
                if time.time() - model_instance.scan_time < 300:
                    try:
                        mac_addr = global_state.arp_cache.get_mac_addr(model_instance.ip)
                    except:
                        mac_addr = "unknown"
                    model_instance.mac = mac_addr
                    # potential problem here:
                    # once a device changes its IP, and a new SSDPInfoModel is created, we will have 2 SSDPInfoModel with same mac addr
                    model_instance.save()

                    common.log(f"[SSDP Scan] Update MAC address {model_instance.mac} for {model_instance.ip}")

    # del scanner and free memory
    del SSDPScannerInstance

    common.log("[SSDP Scan] Exit SSDP scan")
