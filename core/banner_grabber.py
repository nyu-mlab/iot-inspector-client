import threading # DH: Remove unused imports (please use VS Code to identify all unused imports); I won't comment on every single instance of unused imports
import time
from datetime import datetime
import socket
import asyncio
from typing import List
import random
import string
import sys

import core.model as model
import core.common as common
import core.global_state as global_state
import core.config as config


# DH: This doesn't need to be a class. If you're using the object oriented
# design, my assumption is that you're holding certain state within an instance
# -- which is not the case here. So, no need for object oriented design here.
# None of the methods below needs to be associated with a class.
class BannerGrab:

    def __init__(self):

        self.banner_grab_task_send_message = [
            b"GET / HTTP/1.1\r\n\r\n",
            b"HELO example.com\r\n",
            b"USER username\r\n",
            b"SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.1\r\n",
            b"\r\n\r\n",
            b"GET / HTTP/1.0\r\n\r\n",
            b"HELP\r\n"
        ]

        # DH: Make sure that your variable names are descriptive and follows
        # meaningful English grammar. I'd rename this as `result_list`. It's a
        # convention to indicate the type of the variable in the name; e.g.
        # `result_list` instead of `result_collect`.
        self.result_collect = []

    async def async_banner_grab_task(self, target, timeout=5.0):
        banner_collect = []
        ip, port = target
        if isinstance(port, str):
            port = int(port)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)

        # DH: In general, avoid writing loooong methods. Can you break down the steps below into smaller methods? For example, you can rewrite step 1 into a function called `build_tcp_connection` (which returns a socket instance) and step 2 into a function called `wait_for_server_to_send_banner` (which returns a list of banners). This will make your code more readable and easier to maintain.

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
                    # DH: Rename banner_collect as something more meaningful,
                    # e.g., banner_grab_response_status_list or something like that.
                    # Also what do `-1` and `-2` mean? I'd use a string instead
                    # of an integer to indicate the status for readability and
                    # maintainability.
                    banner_collect.append((-1, f"{type(e).__name__} reconnect success"))
                except:
                    common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect fail")
                    banner_collect.append((-1, f"{type(e).__name__} reconnect fail"))
            else:
                common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
                banner_collect.append((-1, f"{type(e).__name__}"))
        else:
            if isinstance(data, bytes): # data[0]:result of asyncio.sleep(3)  data[1]:result of loop.sock_recv(sock, 1024)
                initial_data = data
                common.log(f"[Banner Grab] IP {ip}, Port {port}, Get Initial Data:\n {initial_data.decode('utf-8', errors='ignore') }")
                banner_collect.append((-1, initial_data.decode('utf-8', errors='ignore') ))
                #return {"ip":ip, "port":port, "serive":"null", "banner":initial_data.decode('utf-8', errors='ignore') } # No need for take initiative to send data
            else:
                common.log(f"[Banner Grab] IP {ip}, Port {port}, get wrong inital data = {data}")
                banner_collect.append((-1, "Wrong Initial Data"))


        # STEP 3  Send different bytes to server

        grab_msg_list = [self.generate_random_string(2), self.generate_random_string(32), self.generate_random_string(128), self.generate_random_string(2048)] + self.banner_grab_task_send_message
        for i in range(0, len(grab_msg_list)):
            grab_msg = grab_msg_list[i]
            await asyncio.sleep(1.0)
            try:
                #await asyncio.wait_for(loop.sock_connect(sock, (ip, port)), timeout=5) bad idea
                await asyncio.wait_for(asyncio.get_running_loop().sock_sendall(sock, grab_msg), timeout=5)
                banner = await asyncio.wait_for(asyncio.get_running_loop().sock_recv(sock, 1024), timeout=5)
                common.log(f"[Banner Grab] IP {ip}, Port {port}, Content:\n {banner.decode('utf-8', errors='ignore') }")
                banner_collect.append((i, banner.decode('utf-8', errors='ignore') ))
            except Exception as e:
                if isinstance(e, ConnectionResetError) or isinstance(e, BrokenPipeError):
                    try:
                        await asyncio.sleep(3.0)
                        await asyncio.wait_for(
                            asyncio.get_running_loop().sock_connect(sock, (ip, port)),
                            timeout=3.0
                        )
                        common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__}  reconnect success")
                        banner_collect.append((i, f"{type(e).__name__} reconnect success"))
                    except:
                        common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect fail")
                        banner_collect.append((i, f"{type(e).__name__} reconnect fail"))
                else:
                    common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
                    banner_collect.append((i, f"{type(e).__name__}"))

        sock.close()
        return {"ip":ip, "port":port, "serive":"null", "banner":banner_collect}


    async def async_banner_grab_tasks(self, target_list):

        # Create a list of coroutines for banner grabbing from the given IP and Port lists
        coroutines = []
        for i in range(0, len(target_list)): # here is one-to-one, not double loop!
            coro = self.async_banner_grab_task(target_list[i])
            coroutines.append(coro)

        # Wait for all coroutines to complete and get the results
        results = await asyncio.gather(*coroutines)

        # Update the banner grab info for each IP and Port into _host_state.banner_grab_task_info.append
        self.result_collect += results


    def generate_random_string(self, length):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for _ in range(length)).encode()


    def banner_grab(self, target_list): # potential risk: does not have concurrency control.

            if(len(target_list) == 0):
                common.log("[Banner Grab] No target to grab")
                return

            common.log('[Banner Grab] Start Banner Grab on {} target {}'.format(
                len(target_list),
                ', '.join(str(target) for target in target_list)
            ))

            # DH: No need to check for Python version; we will make sure that all users are using Python 3.8+
            if sys.version_info.major == 3 and sys.version_info.minor >= 7:
                asyncio.run(self.async_banner_grab_tasks(target_list))
            else:
                loop = asyncio.get_event_loop()
                asyncio.set_event_loop(loop)
                asyncio.get_event_loop().run_until_complete(self.async_banner_grab_tasks(target_list))
                loop.close()

            common.log("[Banner Grab] Done")


    # DH: Rename all camelCase to snake_case; e.g. getResult() -> get_result() -- this is the Python convention
    def getResult(self):
        return self.result_collect

    def clearResult(self):
        self.result_collect = []

BANNER_GRAB_INTERVAL = 120

# DH: Move the comment to above the variable; again, this is the Python convention
scan_status_record = {} # {mac1-port1:scan_time1, mac1-port2:scan_time2}


def run_banner_grab(target_device_list = None, target_port_list = None): # target_port_list is List[List], each list for each device
    """
    Banner grab on device's open tcp ports

    """
    # DH: This is a very looong method! Break it up please!
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

        # DH: No need to use a write lockif you're only reading from the
        # database; remove the line below
        with model.write_lock:
            with model.db:

                for device in model.Device.select().where(criteria):
                    target_device_list.append(device)

    # Create scanner
    BannerGrabInstance = BannerGrab()

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
                                common.log(f"[Banner Grab] give up {device.mac_addr}-{str(port)}")
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
        BannerGrabInstance.banner_grab(target_ip_port_list)

        # Aggregate raw results into dict
        raw_results = BannerGrabInstance.getResult()
        this_results = {}
        for entry in raw_results:
            key = entry['port']
            if isinstance(key, int):
                key = str(key)
            value = entry['banner']
            this_results[key] = value

        # Store to DB (simply use dict.update)
        with model.write_lock:
            with model.db:
                # DH: Don't use eval() -- it's a security risk. Use JSON
                # instead. The rest of the codebase uses json.dumps or
                # json.loads.
                known_port_banners = eval(device.port_banners)
                known_port_banners.update(this_results)
                device.port_banners = known_port_banners
                device.save()
                common.log(f"[Banner Grab] IP:{device.ip_addr} Banners:{device.port_banners}")

        # Clear result of this device
        BannerGrabInstance.clearResult()

    # free memory
    # DH: You don't need to do this. Once this method returns, the garbage collector would free up the memory.
    del BannerGrabInstance

    common.log("[Banner Grab] Exit banner grab")