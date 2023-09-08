import time
import socket
import asyncio
import random
import string
import sys

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

def generate_random_string(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length)).encode()

async def async_banner_grab_task(target, timeout=5.0):

    # get ip and port
    ip, port = target
    if isinstance(port, str):
        port = int(port)

    # set socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)

    # store current banner grab result
    this_banner_grab_result_list = []

    # STEP 1  Build TCP Connection
    try:
        # Create a socket object and connect to an IP  and Port.
        await asyncio.wait_for(
            asyncio.get_running_loop().sock_connect(sock, (ip, port)), 
            timeout=3.0
        )
    except Exception as e:
        if isinstance(e, ConnectionResetError) or isinstance(e, BrokenPipeError):
            try:
                await asyncio.sleep(3.0)
                await asyncio.wait_for(
                    asyncio.get_running_loop().sock_connect(sock, (ip, port)), 
                    timeout=3.0
                )
                common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__}  reconnect success")
            except:
                common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
                return {"ip":ip, "port":port, "serive":"null", "banner":[(-2, f"{type(e).__name__}")]}
        else:
            common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
            return {"ip":ip, "port":port, "serive":"null", "banner":[(-2, f"{type(e).__name__}")]}


    # STEP 2  Wait for server to send banner
    try:     
        data = await asyncio.wait_for(
            asyncio.get_running_loop().sock_recv(sock, 1024), 
            timeout=5.0
        )
    except Exception as e:
        if isinstance(e, ConnectionResetError) or isinstance(e, BrokenPipeError):
            try:
                await asyncio.sleep(3.0)
                await asyncio.wait_for(
                    asyncio.get_running_loop().sock_connect(sock, (ip, port)), 
                    timeout=3.0
                )
                common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__}  reconnect success")
                this_banner_grab_result_list.append((-1, f"{type(e).__name__} reconnect success"))
            except:
                common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect fail")
                this_banner_grab_result_list.append((-1, f"{type(e).__name__} reconnect fail"))
        else:
            common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
            this_banner_grab_result_list.append((-1, f"{type(e).__name__}"))
    else:
        if isinstance(data, bytes): # data[0]:result of asyncio.sleep(3)  data[1]:result of loop.sock_recv(sock, 1024)
            initial_data = data
            common.log(f"[Banner Grab] IP {ip}, Port {port}, Get Initial Data:\n {initial_data.decode('utf-8', errors='ignore') }")
            this_banner_grab_result_list.append((-1, initial_data.decode('utf-8', errors='ignore') ))
            #return {"ip":ip, "port":port, "serive":"null", "banner":initial_data.decode('utf-8', errors='ignore') } # No need for take initiative to send data
        else:
            common.log(f"[Banner Grab] IP {ip}, Port {port}, get wrong inital data = {data}")
            this_banner_grab_result_list.append((-1, "Wrong Initial Data"))


    # STEP 3  Send different bytes to server

    grab_msg_list = [generate_random_string(2), generate_random_string(32), generate_random_string(128), generate_random_string(2048)] + banner_grab_request_message
    for i in range(0, len(grab_msg_list)):
        grab_msg = grab_msg_list[i]
        await asyncio.sleep(1.0)
        try:
            #await asyncio.wait_for(loop.sock_connect(sock, (ip, port)), timeout=5) bad idea
            await asyncio.wait_for(asyncio.get_running_loop().sock_sendall(sock, grab_msg), timeout=5)  
            banner = await asyncio.wait_for(asyncio.get_running_loop().sock_recv(sock, 1024), timeout=5) 
            common.log(f"[Banner Grab] IP {ip}, Port {port}, Content:\n {banner.decode('utf-8', errors='ignore') }")
            this_banner_grab_result_list.append((i, banner.decode('utf-8', errors='ignore') ))
        except Exception as e:
            if isinstance(e, ConnectionResetError) or isinstance(e, BrokenPipeError):
                try:
                    await asyncio.sleep(3.0)
                    await asyncio.wait_for(
                        asyncio.get_running_loop().sock_connect(sock, (ip, port)),
                        timeout=3.0
                    )
                    common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__}  reconnect success")
                    this_banner_grab_result_list.append((i, f"{type(e).__name__} reconnect success"))
                except:
                    common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect fail")
                    this_banner_grab_result_list.append((i, f"{type(e).__name__} reconnect fail"))
            else:
                common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
                this_banner_grab_result_list.append((i, f"{type(e).__name__}"))
        
    sock.close()
    return {"ip":ip, "port":port, "serive":"null", "banner":this_banner_grab_result_list}



async def async_banner_grab_tasks(target_list):

    # Create a list of coroutines for banner grabbing from the given IP and Port lists
    coroutines = []
    for i in range(0, len(target_list)): # here is one-to-one, not double loop!
        coro = async_banner_grab_task(target_list[i])
        coroutines.append(coro)

    # Wait for all coroutines to complete and get the results
    results = await asyncio.gather(*coroutines)

    return results


def banner_grab(target_list): # potential risk: does not have concurrency control.

    if(len(target_list) == 0):
        common.log("[Banner Grab] No target port to grab")
        return []

    common.log('[Banner Grab] Start Banner Grab on {} target {}'.format(
        len(target_list), 
        ', '.join(str(target) for target in target_list)
    ))
    if sys.version_info.major == 3 and sys.version_info.minor >= 7:
        results = asyncio.run(async_banner_grab_tasks(target_list))
    else:
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        results = asyncio.get_event_loop().run_until_complete(async_banner_grab_tasks(target_list))
        loop.close()

    common.log("[Banner Grab] Done")
    return results


BANNER_GRAB_INTERVAL = 120
scan_status_record = {} # {mac1-port1:scan_time1, mac1-port2:scan_time2} 

def run_banner_grab(target_device_list = None, target_port_list = None): # target_port_list is List[List], each list for each device
    """
    Banner grab on device's open tcp ports

    """
    if not global_state.is_inspecting:
        return

    # Check the consent
    if not config.get('has_consented_to_overall_risks', False):
        return

    if target_port_list != None:
        if (target_device_list == None) or (len(target_device_list) != len(target_port_list)):
            common.log("[Banner Grab] Args not qualified!")
            return

    # Define target to scan
    if target_device_list == None:

        target_device_list = []
        criteria = (model.Device.is_inspected == 1) & (model.Device.ip_addr != '')

        with model.write_lock:
            with model.db:

                for device in model.Device.select().where(criteria):
                    target_device_list.append(device)


    if len(target_device_list) == 0:
        common.log("[Banner Grab] No valid target device to scan")
        return

    # Run it one by one
    for i in range(0, len(target_device_list)):
        device = target_device_list[i]

        # Make sure that the device is in the ARP cache; if not, skip
        try:
            global_state.arp_cache.get_ip_addr(device.mac_addr)
        except KeyError:
            continue

        target_ip_port_list = []

        # Build target list
        if target_port_list == None:

            with model.write_lock:
                with model.db:
                    ip = device.ip_addr
                    ports = eval(device.open_tcp_ports)
                    for port in ports:

                        if (device.mac_addr+"-"+str(port)) in scan_status_record:
                            if time.time() - scan_status_record[(device.mac_addr+"-"+str(port))] < BANNER_GRAB_INTERVAL:
                                common.log(f"[Banner Grab] give up {device.mac_addr} {ip}:{str(port)}")
                                continue

                        target_ip_port_list.append((ip, port))
                        scan_status_record[(device.mac_addr+"-"+str(port))] = time.time()
        else:

            with model.write_lock:
                with model.db:
                    ip = device.ip_addr

            for port in target_port_list[i]:
                target_ip_port_list.append((ip, port))
                scan_status_record[(device.mac_addr+"-"+str(port))] = time.time()

        # Run the banner grab
        results = banner_grab(target_ip_port_list)

        # 
        if len(results) > 0:

            # Aggregate raw results into dict
            this_results = {}
            for entry in results:
                key = entry['port']
                if isinstance(key, int):
                    key = str(key)
                value = entry['banner']
                this_results[key] = value


            # Store to DB (simply use dict.update)
            with model.write_lock:
                with model.db:
                    
                    known_port_banners = eval(device.port_banners)
                    known_port_banners.update(this_results)
                    device.port_banners = known_port_banners
                    device.save()
                    common.log(f"[Banner Grab] IP:{device.ip_addr} Banners:{device.port_banners}")

    common.log("[Banner Grab] Exit banner grab")