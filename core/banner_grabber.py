import time
import socket
import asyncio
import random
import string
import json

import core.model as model
import core.common as common
import core.global_state as global_state
import core.config as config

banner_grab_request_message = [
    b"GET / HTTP/1.1\r\n\r\n",
    b"HELO example.com\r\n",
    b"USER username\r\n",
    b"SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.1\r\n",
    b"\r\n\r\n",
    b"GET / HTTP/1.0\r\n\r\n",
    b"HELP\r\n"
]

# TCP connection state
CONNECT_SUCCESS = 0
RECONNECT_SUCCESS = 1
RECONNECT_EXCEPTION = 2
OTHER_EXCEPTION = 3

# Set minimal scan interval to avoid too frequent scan
BANNER_GRAB_INTERVAL = 120
# {mac1-port1:scan_time1, mac1-port2:scan_time2} 
last_scan_time_record = {}


def generate_random_string(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length)).encode()


async def talk_to_target(ip, port, sock, timeout = 5.0, step = "Unknown", req="", recv=False):
    """ Send request and receive response through socket """

    try:
        # If request message is given, send request to targets
        if req != "":
            await asyncio.wait_for(asyncio.get_running_loop().sock_sendall(sock, req), timeout=timeout)

        # If recv == "True", receive banner from the target
        if recv == True:
            resp = await asyncio.wait_for(asyncio.get_running_loop().sock_recv(sock, 1024), timeout=timeout)
            common.log(f"[Banner Grab] IP {ip}, Port {port}, Step {step}, Result = Receivce banner as below:\n{resp.decode('utf-8', errors='ignore')}")
            return CONNECT_SUCCESS, resp.decode('utf-8', errors='ignore')
        # If recv == "False", we just build TCP connection only
        else:
            await asyncio.wait_for(asyncio.get_running_loop().sock_connect(sock, (ip, port)), timeout=timeout)
            common.log(f"[Banner Grab] IP {ip}, Port {port}, Step {step}, Result = Build TCP connection success")
            return CONNECT_SUCCESS, "Build TCP connection success"

    except Exception as e:
        # We try to rebuild the TCP connection if the exception is ConnectionResetError or BrokenPipeError
        if isinstance(e, ConnectionResetError) or isinstance(e, BrokenPipeError):
            try:
                await asyncio.sleep(timeout)
                await asyncio.wait_for( asyncio.get_running_loop().sock_connect(sock, (ip, port)), timeout=timeout)
                common.log(f"[Banner Grab] IP {ip}, Port {port}, Step {step}, Result = {type(e).__name__}  reconnect success")
                return RECONNECT_SUCCESS, f"{type(e).__name__}"
            except:
                pass
        # No need to reconnect or reconnect failure
        common.log(f"[Banner Grab] IP {ip}, Port {port}, Step {step}, Result = {type(e).__name__}-{str(e)}")
        return OTHER_EXCEPTION, f"{type(e).__name__}"


async def async_banner_grab_task(target_ip_port, timeout=5.0):
    """ Banner grab on one ip:port """

    # Get ip and port
    ip, port = target_ip_port
    if isinstance(port, str):
        port = int(port)

    # Set socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)

    # Store current banner grab result
    this_result = {"ip":ip, "port":port, "serive":"null", "banner":[]}

    # STEP 1 Build TCP Connection
    step = "Building TCP Connetion"
    state, resp = await talk_to_target(ip, port, sock, timeout=timeout, step=step)
    this_result['banner'].append((step, resp))

    # If failed to build connection, return directly
    if state == RECONNECT_EXCEPTION or state == OTHER_EXCEPTION:
        return this_result

    # STEP 2  Wait for server to send banner
    step = "Receiving Server Banner"
    state, resp = await talk_to_target(ip, port, sock, timeout=timeout, step=step, recv=True)
    this_result['banner'].append((step, resp))

    # STEP 3  Send different bytes to server
    this_request_messages = [generate_random_string(2), generate_random_string(32), generate_random_string(128), generate_random_string(2048)] + banner_grab_request_message

    for i in range(0, len(this_request_messages)):
        await asyncio.sleep(timeout/5)

        step = f"Requesting Banner {i}"
        state, resp = await talk_to_target(ip, port, sock, timeout=timeout, step=step, req=this_request_messages[i], recv=True)
        this_result['banner'].append((i, resp))

        if state == RECONNECT_EXCEPTION or state == OTHER_EXCEPTION:
            await asyncio.sleep(timeout/2)

    # Exit
    sock.close()
    return this_result


async def async_banner_grab_tasks(target_ip_port_list):
    """ Control different async banner tasks"""

    # Create a list of coroutines for banner grabbing from the given IP and Port lists
    coroutines = []
    for i in range(0, len(target_ip_port_list)): # here is one-to-one, not double loop!
        coro = async_banner_grab_task(target_ip_port_list[i])
        coroutines.append(coro)

    # Wait for all coroutines to complete and get the results
    results = await asyncio.gather(*coroutines)

    return results


def banner_grab(target_ip_port_list):
    """ Launch banner grab """

    if(len(target_ip_port_list) == 0):
        common.log("[Banner Grab] No target to grab for this device")
        return []

    common.log('[Banner Grab] Start Banner Grab on {} target {}'.format(
        len(target_ip_port_list),
        ', '.join(str(target) for target in target_ip_port_list)
    ))

    # Since one device is unlikely to have too many open TCP ports
    # The concurrency level is equal to the number of open TCP ports
    result = asyncio.run(async_banner_grab_tasks(target_ip_port_list))

    common.log("[Banner Grab] Done")
    return result


def get_current_devices():
    """ Get known valid devices """

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
            ports = eval(device.open_tcp_ports)
            for port in ports:

                if (device.mac_addr+"-"+str(port)) in last_scan_time_record:
                    if time.time() - last_scan_time_record[(device.mac_addr+"-"+str(port))] < BANNER_GRAB_INTERVAL:
                        common.log(f"[Banner Grab] give up too frequent scan {device.mac_addr} {ip}:{str(port)}")
                        continue

                target_ip_port_list.append((ip, port))
                last_scan_time_record[(device.mac_addr+"-"+str(port))] = time.time()
    else:
        for port in target_port_list:
            target_ip_port_list.append((ip, port))
            last_scan_time_record[(device.mac_addr+"-"+str(port))] = time.time()

    return target_ip_port_list


def store_result_to_database(device, result):
    """ Store banner grab result for one device """

    # Aggregate raw results into dict
    this_result = {}
    for entry in result:
        key = entry['port']
        if isinstance(key, int):
            key = str(key)
        value = entry['banner']
        this_result[key] = value

    # Store to DB (simply use dict.update)
    with model.write_lock:
        with model.db:

            known_port_banners = json.loads(device.port_banners)
            common.log(f"[Banner Grab] From database get IP:{device.ip_addr} Banners:{known_port_banners}")

            known_port_banners.update(this_result)
            device.port_banners = json.dumps(known_port_banners)

            device.save()
            common.log(f"[Banner Grab] Store to database IP:{device.ip_addr} Banners:{device.port_banners}")


def run_banner_grab(target_device_list = None, target_ports_list = None): 
    """ Main API for Banner grab on device's open tcp ports """

    if not global_state.is_inspecting:
        return

    # Check the consent
    if not config.get('has_consented_to_overall_risks', False):
        return

    # target_ports_list is List[List], each list for each device
    # port_list and device_list must be one-to-one relation
    if target_ports_list != None:
        if (target_device_list == None) or (len(target_device_list) != len(target_ports_list)):
            common.log("[Banner Grab] Args not qualified!")
            return

    # Define target devices to scan
    if target_device_list == None:
        target_device_list = get_current_devices()

    if len(target_device_list) == 0:
        common.log("[Banner Grab] No valid target device to scan")
        return

    # Run banner grab on each device one by one
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

        # Run the banner grab
        result = banner_grab(target_ip_port_list)

        # Store the result of this device to database
        if len(result) > 0:
            store_result_to_database(device, result)

    common.log("[Banner Grab] Exit banner grab")