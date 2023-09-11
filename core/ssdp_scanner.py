# some codes come from https://github.com/tenable/upnp_info and https://paper.seebug.org/1727/#0x03-ssdp

import re
import time
import socket
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import json

import core.model as model
import core.common as common
import core.global_state as global_state
import core.config as config

TIME_OUT = 5

# The class used to store the data of SSDP information
class SSDPInfo():

    def __init__(self):

        self.scan_time = 0

        self.location = ""
        self.ip = ""
        self.port = ""
        self.outer_file_name = ""

        self.original_reply = []

        self.server_string = ""
        self.device_type = ""
        self.friendly_name = ""
        self.manufacturer = ""
        self.manufacturer_url = ""
        self.model_description = ""
        self.model_name = ""
        self.model_number = ""

        self.services_list = []


###
# Send a multicast message tell all the pnp services that we are looking
# For them. Keep listening for responses until we hit a TIME_OUT second timeout (yes,
# this could technically cause an infinite loop). Parse the URL out of the
# 'location' field in the HTTP header and store for later analysis.
#
# @return the list of advertised upnp locations, IPs, and original_replys
###
def discover_pnp_locations():
    common.log('[SSDP Scan] Discovering UPnP locations')

    # xml file locations extracted from SSDP response
    locations = []
    # {location:[reply1, reply2]}
    original_replys = {}

    location_regex = re.compile("location:[ ]*(.+)\r\n", re.IGNORECASE)
    ssdpDiscover = ('M-SEARCH * HTTP/1.1\r\n' +
                    'HOST: 239.255.255.250:1900\r\n' +
                    'MAN: "ssdp:discover"\r\n' +
                    'MX: 1\r\n' +
                    'ST: ssdp:all\r\n' +
                    '\r\n')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(ssdpDiscover.encode('ASCII'), ("239.255.255.250", 1900))
    sock.settimeout(TIME_OUT)

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            location_result = location_regex.search(data.decode('utf-8'))
            # new location, add to locations and create an entry in original_replys dict
            if location_result and (location_result.group(1) in locations) == False:
                locations.append(location_result.group(1))
                original_replys[location_result.group(1)] = [data.decode('utf-8')]
            # old location but another response, add to original_replys dict
            elif location_result:
                original_replys[location_result.group(1)].append(data.decode('utf-8'))
            else:
                common.log(f"[SSDP Scan] Unknown reply: {type(data.decode('utf-8'))}\n{data.decode('utf-8')}")

    except socket.error:
        sock.close() # Exit while loop with exception, so this line will always been executed

    common.log('[SSDP Scan] %d locations found:' % len(locations))
    for location in locations:
        common.log('[SSDP Scan]\t%s' % location)

    return locations, original_replys

##
# Tries to print an element extracted from the XML.
# @param xml the xml tree we are working on
# @param xml_name the name of the node we want to pull text from
# @param print_name the name we want to appear in stdout
##
def print_attribute(xml, xml_name, print_name):
    try:
        temp = xml.find(xml_name).text
        common.log('[SSDP Scan]\t-> %s: %s' % (print_name, temp))
        return temp
    except AttributeError:
        return None


def create_basic_ssdp_info(location, original_replys):

    ssdp_info = SSDPInfo()

    # Set location, response content and scan time
    ssdp_info.location = location
    ssdp_info.original_reply = original_replys[location]
    ssdp_info.scan_time = time.time()

    # Set ip, port and file name
    match = re.search(r"http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)/(.*)", location)
    if match:
        ssdp_info.ip = match.group(1)
        ssdp_info.port = match.group(2)
        ssdp_info.outer_file_name = match.group(3)

    return ssdp_info


def parse_resp_server_string_to_ssdp_info(resp, ssdp_info):
    if resp.headers.get('server'):
        server_string = resp.headers.get('server')
        common.log('[SSDP Scan] \t-> Server String: %s' % server_string)
        ssdp_info.server_string = server_string
    else:
        common.log('[SSDP Scan] \t-> No server string')


def parse_xml_device_info_to_ssdp_info(xml_root, ssdp_info):
    ssdp_info.device_type = print_attribute(xml_root, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}deviceType", "Device Type")
    ssdp_info.friendly_name = print_attribute(xml_root, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}friendlyName", "Friendly Name")
    ssdp_info.manufacturer = print_attribute(xml_root, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}manufacturer", "Manufacturer")
    ssdp_info.manufacturer_url = print_attribute(xml_root, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}manufacturerURL", "Manufacturer URL")
    ssdp_info.model_description = print_attribute(xml_root, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelDescription", "Model Description")
    ssdp_info.model_name = print_attribute(xml_root, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelName", "Model Name")
    ssdp_info.model_number = print_attribute(xml_root, "./{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelNumber", "Model Number")


def parse_single_service_info_to_ssdp_info(service, parsed):
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

    # Read in the SCP XML
    resp = requests.get(serviceURL, timeout=TIME_OUT)
    try:
        serviceXML = ET.fromstring(resp.text)
        actions = serviceXML.findall(".//*{urn:schemas-upnp-org:service-1-0}action")
        for action in actions:
            action_name = action.find('./{urn:schemas-upnp-org:service-1-0}name').text
            common.log(f'[SSDP Scan]\t\t\t- {action_name}')
            this_service["actions"].append(action_name)
    except:
        common.log('[SSDP Scan]\t\t\t[!] Failed to parse the service response XML')

    return this_service


def parse_location_xml_to_ssdp_info(location, ssdp_info):

    # Step 1: fetch xml file
    resp = requests.get(location, timeout=TIME_OUT)

    # Step 1.5: get server string info from the response
    parse_resp_server_string_to_ssdp_info(resp, ssdp_info)

    # Step 2: read xml file
    parsed = urlparse(location)
    common.log('[SSDP Scan]\t==== XML Attributes ===')
    try:
        xml_root = ET.fromstring(resp.text)
    except:
        common.log('[SSDP Scan]\t Failed XML parsing of %s' % location)
        return

    # Step 3: parse infomation related to device
    parse_xml_device_info_to_ssdp_info(xml_root, ssdp_info)

    # Step 4: parse multiply services one by one
    common.log('[SSDP Scan]\t-> Services:')
    services = xml_root.findall(".//*{urn:schemas-upnp-org:device-1-0}serviceList/")
    for service in services:
        this_service = parse_single_service_info_to_ssdp_info(service, parsed)
        ssdp_info.services_list.append(this_service)


###
# Loads the XML at each location and prints out the API along with some other
# interesting data.
#
# @param locations a collection of URLs
# @return igd_ctr (the control address) and igd_service (the service type)
###
def parse_locations(locations, original_replys):
    if len(locations) < 1:
        common.log('[SSDP Scan] No location to parse')
        return []

    common.log('[SSDP Scan] Start parse %d locations:' % len(locations))
    result_list = []

    for i in range(0, len(locations)):
        location = locations[i]
        common.log('[SSDP Scan] Loading %s...' % location)

        ssdp_info = create_basic_ssdp_info(location, original_replys)

        try:
            # Fetch the xml file and parse it. Store parsed infomation to ssdp_info
            parse_location_xml_to_ssdp_info(location, ssdp_info)

        except requests.exceptions.ConnectionError:
            common.log('[SSDP Scan] Could not load %s' % location)
        except requests.exceptions.ReadTimeout:
            common.log('[SSDP Scan] Timeout reading from %s' % location)
        except Exception as e:
            common.log(f'[SSDP Scan] Error parsing location {e}')

        result_list.append(ssdp_info)

    common.log("[SSDP Scan] Done Parsing")
    return result_list


def scan():
    """ Launch SSDP scan """
    common.log("[SSDP Scan] Start.")
    locations, original_replys = discover_pnp_locations()
    result_list = parse_locations(locations, original_replys)
    common.log("[SSDP Scan] Finish.")
    return result_list


def assign_mac_for_unknown():
    """
    Some SSDP entry in database have unknown MAC because SSDP scan may be faster than ARP to discover devices.
    Now we try to fix this gap. Every time SSDP scan is called, we do this function.
    """
    with model.write_lock:
        with model.db:
            # using global_state.arp_cache to bind ip to mac.
            # also update for those found in previous rounds except for those scanned in more than 5 mins ago
            for model_instance in model.SSDPInfoModel.select().where(model.SSDPInfoModel.mac == "unknown"):
                last_scan_time = model_instance.scan_time
                if (time.time() - last_scan_time) < 300:
                    try:
                        mac_addr = global_state.arp_cache.get_mac_addr(model_instance.ip)
                        model_instance.mac = mac_addr
                        model_instance.save()
                        common.log(f"[SSDP Scan] Assign MAC address {model_instance.mac} for {model_instance.ip}")
                    except:
                        common.log(f"[SSDP Scan] Unknown MAC for {model_instance.ip}, scan_time {last_scan_time}")


def store_result_to_database(result_list):

    assign_mac_for_unknown()

    with model.write_lock:
        with model.db:

            for SSDPInfoInst in result_list:

                try:
                    mac_addr = global_state.arp_cache.get_mac_addr(model_instance.ip)
                    model_instance = model.SSDPInfoModel.get_or_none(mac=mac_addr)
                except:
                    # We leave it for now and deal with it in next round assign_mac_for_unknown()
                    mac_addr="unknown" 
                    model_instance = model.SSDPInfoModel.get_or_none(ip=SSDPInfoInst.ip, port=SSDPInfoInst.port)

                # Create a new entry in database
                if model_instance is None:
                    model.SSDPInfoModel.create(
                        mac = mac_addr,
                        scan_time = SSDPInfoInst.scan_time,
                        location = SSDPInfoInst.location,
                        ip = SSDPInfoInst.ip,
                        port = SSDPInfoInst.port,
                        outer_file_name = SSDPInfoInst.outer_file_name,
                        original_reply = json.dumps(SSDPInfoInst.original_reply),

                        server_string = SSDPInfoInst.server_string,
                        device_type = SSDPInfoInst.device_type,
                        friendly_name = SSDPInfoInst.friendly_name,
                        manufacturer = SSDPInfoInst.manufacturer,
                        manufacturer_url = SSDPInfoInst.manufacturer_url,
                        model_description = SSDPInfoInst.model_description,
                        model_name = SSDPInfoInst.model_name,
                        model_number = SSDPInfoInst.model_number,
                        services_list = json.dumps(SSDPInfoInst.services_list)
                    )
                    common.log(f"[SSDP Scan] Create new ssdp info for {mac_addr} {SSDPInfoInst.ip}:{SSDPInfoInst.port}")

                # Update existing entry in database
                else:
                    model_instance.mac = mac_addr
                    model_instance.scan_time = SSDPInfoInst.scan_time
                    model_instance.location = SSDPInfoInst.location
                    model_instance.ip = SSDPInfoInst.ip
                    model_instance.port = SSDPInfoInst.port
                    model_instance.outer_file_name = SSDPInfoInst.outer_file_name
                    model_instance.original_reply = json.dumps(SSDPInfoInst.original_reply)

                    model_instance.server_string = SSDPInfoInst.server_string
                    model_instance.device_type = SSDPInfoInst.device_type
                    model_instance.friendly_name = SSDPInfoInst.friendly_name
                    model_instance.manufacturer = SSDPInfoInst.manufacturer
                    model_instance.manufacturer_url = SSDPInfoInst.manufacturer_url
                    model_instance.model_description = SSDPInfoInst.model_description
                    model_instance.model_name = SSDPInfoInst.model_name
                    model_instance.model_number = SSDPInfoInst.model_number
                    model_instance.services_list = json.dumps(SSDPInfoInst.services_list)

                    model_instance.save()
                    common.log(f"[SSDP Scan] Update ssdp info for {SSDPInfoInst.ip}:{SSDPInfoInst.port}")


def run_ssdp_scan():
    """ Main API for scan SSDP infos """

    if not global_state.is_inspecting:
        return

    # Check the consent
    if not config.get('has_consented_to_overall_risks', False):
        return

    # Run SSDP scan
    # It will block until no more response show up within given time
    result_list = scan() 

    # save data to DB
    store_result_to_database(result_list)

    # Exit
    common.log("[SSDP Scan] Exit SSDP scan")