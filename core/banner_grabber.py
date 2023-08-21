import threading
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

        self.result_collect = []

    async def async_banner_grab_task(self, target, timeout=5.0):
        banner_collect = []
        ip, port = target
        if isinstance(port, str):
            print(port)
            port = int(port)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)

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
                    print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect success")
                    common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__}  reconnect success")
                except:
                    print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
                    common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
                    return {"ip":ip, "port":port, "serive":"null", "banner":[(-2, f"{type(e).__name__}")]}
            else:
                print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
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
                    print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect success")
                    common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__}  reconnect success")
                    banner_collect.append((-1, f"{type(e).__name__} reconnect success"))
                except:
                    print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect fail")
                    common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect fail")
                    banner_collect.append((-1, f"{type(e).__name__} reconnect fail"))
            else:
                print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
                common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
                banner_collect.append((-1, f"{type(e).__name__}"))
        else:
            if isinstance(data, bytes): # data[0]:result of asyncio.sleep(3)  data[1]:result of loop.sock_recv(sock, 1024)
                initial_data = data
                common.log(f"[Banner Grab] IP {ip}, Port {port}, Get Initial Data:\n {initial_data.decode('utf-8', errors='ignore') }")
                print(f"[Banner Grab] IP {ip}, Port {port}, Get Initial Data:\n {initial_data.decode('utf-8', errors='ignore') }")
                banner_collect.append((-1, initial_data.decode('utf-8', errors='ignore') ))
                #return {"ip":ip, "port":port, "serive":"null", "banner":initial_data.decode('utf-8', errors='ignore') } # No need for take initiative to send data
            else:
                print(f"[Banner Grab] IP {ip}, Port {port}, get wrong inital data = {data}")
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
                print(f"[Banner Grab] IP {ip}, Port {port}, Content:\n {banner.decode('utf-8', errors='ignore') }")
                banner_collect.append((i, banner.decode('utf-8', errors='ignore') ))
            except Exception as e:
                if isinstance(e, ConnectionResetError) or isinstance(e, BrokenPipeError):
                    try:
                        await asyncio.sleep(3.0)
                        await asyncio.wait_for(
                            asyncio.get_running_loop().sock_connect(sock, (ip, port)), 
                            timeout=3.0
                        )
                        print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect success")
                        common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__}  reconnect success")
                        banner_collect.append((i, f"{type(e).__name__} reconnect success"))
                    except:
                        print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect fail")
                        common.log(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} reconnect fail")
                        banner_collect.append((i, f"{type(e).__name__} reconnect fail"))
                else:
                    print(f"[Banner Grab] IP {ip}, Port {port}: {type(e).__name__} - {str(e)}")
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
                print("[Banner Grab] No target to grab")
                common.log("[Banner Grab] No target to grab")
                return 

            common.log('[Banner Grab] Start Banner Grab on {} target {}'.format(
                len(target_list), 
                ', '.join(str(target) for target in target_list)
            ))
            print('[Banner Grab] Start Banner Grab on {} target {}'.format(
                len(target_list), 
                ', '.join(str(target) for target in target_list)
            ))

            if sys.version_info.major == 3 and sys.version_info.minor >= 7:
                asyncio.run(self.async_banner_grab_tasks(target_list))
            else:
                loop = asyncio.get_event_loop()
                asyncio.set_event_loop(loop)
                asyncio.get_event_loop().run_until_complete(self.async_banner_grab_tasks(target_list))
                loop.close()

            print("[Banner Grab] Done")
            common.log("[Banner Grab] Done")


    def getResult(self):
        return self.result_collect
            
    def clearResult(self):
        self.result_collect = []


def run_banner_grab(target_device_list = None, target_port_list = None): # target_port_list is List[List], each list for each device
    """
    Banner grab on device's open tcp ports

    """
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

    # Create scanner
    BannerGrabInstance = BannerGrab()

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
                        target_ip_port_list.append((ip, port))
        else:

            with model.write_lock:
                with model.db:
                    ip = device.ip_addr
                    
            for port in target_port_list[i]:
                target_ip_port_list.append((ip, port))
        
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
                
                known_port_banners = eval(device.port_banners)
                known_port_banners.update(this_results)
                device.port_banners = known_port_banners
                device.save()
                print(f"IP:{device.ip_addr} Banners:{device.port_banners}")
                common.log(f"IP:{device.ip_addr} Banners:{device.port_banners}")

        # Clear result of this device
        BannerGrabInstance.clearResult()

    # free memory
    del BannerGrabInstance

    print("[Banner Grab] Exit")