import sys
from socket import socket, AF_INET, SOCK_STREAM
import time
import asyncio
from asyncio import Queue, TimeoutError, gather
from typing import List
import random
import scapy.all as sc
from async_timeout import timeout
import itertools


import core.model as model
import core.common as common
import core.global_state as global_state
import core.config as config

class TCPScanner():

    def __init__(self, time_out = 5.0, concurrency = 500):

        self.result = []
        self.error = []

        self.timeout = time_out
        self.concurrency = concurrency
        
        self.result_collect = []

    async def scan_task(self):
        while True:
            t1 = time.time()
            ip_port = await self.queue.get()
            ip, port = ip_port
            #print(ip, port)
            sock = socket(AF_INET, SOCK_STREAM)
            sock.setblocking(False) # May be detrimental for low performance device
            try:
                if sys.version_info.major == 3 and sys.version_info.minor >= 7:
                    async with timeout(self.timeout):
                        await asyncio.get_event_loop().sock_connect(sock, (ip, port))
                        t2 = time.time()
                        if sock:
                            self.result_collect.append((ip, port))
                            print("[TCP Scan]", time.strftime('%Y-%m-%d %H:%M:%S'), ip, port, 'open', round(t2 - t1, 2))
                else:
                    with timeout(self.timeout):
                        await asyncio.get_event_loop().sock_connect(sock, (ip, port))
                        t2 = time.time()
                        if sock:
                            self.result_collect.append((ip, port))
                            print("[TCP Scan]", time.strftime('%Y-%m-%d %H:%M:%S'), ip, port, 'open', round(t2 - t1, 2))
                sock.close()
            # we have to deal with the exception, otherwise this task will stop
            except:
                #self.error.append((ip, port))
                #print("exception")
                sock.close()
            self.queue.task_done()
            #print("done")

    async def async_scan_tasks(self, target_ip, target_port_list):

        self.queue = Queue()
        #print("new queue")

        for port in target_port_list:
            self.queue.put_nowait((target_ip, port))

        tasks = [asyncio.get_event_loop().create_task(self.scan_task()) for _ in range(self.concurrency)]
        # If the queue is not empty, it will always block here
        await self.queue.join()
        # Exit one by one
        for task in tasks:
            task.cancel()
        # Wait until all worker tasks are cancelled.
        await gather(*tasks, return_exceptions=True)

    def split_array(self, array, chunk_size):
        result = []
        for i in range(0, len(array), chunk_size):
            result.append(array[i:i+chunk_size])
        return result
    
    def get_popular_port_list(self):

        # Ports collected from common IoT services and protocols
        # from redhat scans, captured traffic, and home IoT scans.
        port_set = set([2121, 11111, 1137, 123, 137, 139, 1443, 1698, 1743, 18181, 1843,
                        1923, 19531, 22, 25454, 2869, 32768, 32769, 35518, 35682,
                        36866, 3689, 37199, 38576, 41432, 42758, 443, 445, 45363,
                        4548, 46355, 46995, 47391, 48569, 49152, 49153, 49154,
                        49451, 53, 5353, 548, 554, 56167, 56278, 56789, 56928,
                        59815, 6466, 6467, 655, 7676, 7678, 7681, 7685, 7777, 81,
                        8181, 8187, 8222, 8443, 88, 8842, 8883, 8886, 8888, 8889,
                        911, 9119, 9197, 9295, 9999, 443, 80, 993, 5228, 4070,
                        5223, 9543, 1, 2, 4, 5, 6, 7, 9, 11, 13, 15, 17, 18, 19,
                        20, 21, 22, 23, 25, 37, 39, 42, 43, 49, 50, 53, 63, 67, 68,
                        69, 70, 71, 72, 73, 79, 80, 81, 88, 95, 98, 101, 102, 105,
                        106, 107, 109, 110, 111, 113, 115, 117, 119, 123, 137, 138,
                        139, 143, 161, 162, 163, 164, 174, 177, 178, 179, 191, 194,
                        199, 201, 202, 204, 206, 209, 210, 213, 220, 245, 347, 363,
                        369, 370, 372, 389, 427, 434, 435, 443, 444, 445, 464, 465,
                        468, 487, 488, 496, 500, 512, 513, 514, 515, 517, 518, 519,
                        520, 521, 525, 526, 530, 531, 532, 533, 535, 538, 540, 543,
                        544, 546, 547, 548, 554, 556, 563, 565, 587, 610, 611, 612,
                        616, 631, 636, 655, 674, 694, 749, 750, 751, 752, 754, 760,
                        765, 767, 808, 871, 873, 901, 911, 953, 992, 993, 994, 995,
                        1080, 1109, 1127, 1137, 1178, 1236, 1300, 1313, 1433, 1434,
                        1443, 1494, 1512, 1524, 1525, 1529, 1645, 1646, 1649, 1698,
                        1701, 1718, 1719, 1720, 1743, 1758, 1759, 1789, 1812, 1813,
                        1843, 1911, 1923, 1985, 1986, 1997, 2003, 2049, 2053, 2102,
                        2103, 2104, 2105, 2121, 2150, 2401, 2430, 2431, 2432, 2433,
                        2600, 2601, 2602, 2603, 2604, 2605, 2606, 2809, 2869, 2988,
                        3128, 3130, 3306, 3346, 3455, 3689, 4011, 4070, 4321, 4444,
                        4548, 4557, 4559, 5002, 5223, 5228, 5232, 5308, 5353, 5354,
                        5355, 5432, 5680, 5999, 6000, 6010, 6466, 6467, 6667, 7000,
                        7001, 7002, 7003, 7004, 7005, 7006, 7007, 7008, 7009, 7100,
                        7666, 7676, 7678, 7681, 7685, 7777, 8008, 8080, 8081, 8181,
                        8187, 8222, 8443, 8842, 8883, 8886, 8888, 8889, 9100, 9119,
                        9197, 9295, 9359, 9543, 9876, 9999, 10080, 10081, 10082,
                        10083, 11111, 11371, 11720, 13720, 13721, 13722, 13724,
                        13782, 13783, 18181, 19531, 20011, 20012, 22273, 22289,
                        22305, 22321, 24554, 25454, 26000, 26208, 27374, 32768,
                        32769, 33434, 35518, 35682, 36866, 37199, 38576, 41432,
                        42758, 45363, 46355, 46995, 47391, 48569, 49152, 49153,
                        49154, 49451, 56167, 56278, 56789, 56928, 59815, 60177,
                        8060, # Roku
                        60179])
        return sorted(port_set)

    def scan(self, target_ip_list, scanAll = False):
        

        if len(target_ip_list) == 0:
            print("[TCP Scan] No target to scan")
            common.log("[TCP Scan] No target to scan")
            return
        
        print('[TCP Scan] Start scanning {} IPs: {}'.format(
            len(target_ip_list),
            ', '.join(target_ip_list)
        ))
        common.log('[TCP Scan] Start scanning {} IPs: {}'.format(
            len(target_ip_list),
            ', '.join(target_ip_list)
        ))

        if scanAll == True:
            print("[TCP Scan] Scan 65K ports")
            common.log("[TCP Scan] Scan 65K ports")
        else:
            print("[TCP Scan] Scan popular ports")
            common.log("[TCP Scan] Scan popular ports")

        if scanAll == True:
            all_port_list = [i for i in range(1, 65536)]
            split_port_list = self.split_array(all_port_list, 5000) 
        else:
            split_port_list = [self.get_popular_port_list()]

        for ip in target_ip_list:
            print("[TCP Scan] Start scan on ip =", ip)
            
            for batch_port_list in split_port_list:

                random.shuffle(batch_port_list)
                
                last_one = batch_port_list[-1]
                start_time = time.time()

                if sys.version_info.major == 3 and sys.version_info.minor >= 7:
                    asyncio.run(self.async_scan_tasks(ip, batch_port_list))
                else:
                    asyncio.get_event_loop().run_until_complete(self.async_scan_tasks(ip, batch_port_list))
                
                print("[TCP Scan] Last one of this batch:", ip, str(last_one))
                print(f'[TCP Scan] Time for this batch: {time.time() - start_time:.2f}')

                # If you dont like scan too fast
                # time_used = time.time() - start_time
                # if time_used < 10:
                #     time.sleep(3)

    def getResult(self):
        return self.result_collect
            
    def clearResult(self):
        self.result_collect = []


def run_tcp_scan(target_device_list = None, scanAll = False):

    # Define target to scan
    if target_device_list == None:

        inspected_device_list = []
        criteria = (model.Device.is_inspected == 1) & (model.Device.ip_addr != '')

        with model.write_lock:
            with model.db:

                for device in model.Device.select().where(criteria):
                    inspected_device_list.append(device)

        target_device_list = inspected_device_list.copy()

    # Create scanner
    TCPScannerInstance = TCPScanner()

    # Run it one by one
    for device in target_device_list:

        # Make sure that the device is in the ARP cache; if not, skip
        try:
            global_state.arp_cache.get_ip_addr(device.mac_addr)
        except KeyError:
            continue
        
        # run scan on target
        TCPScannerInstance.scan([device.ip_addr], scanAll)

        # Get scanner result
        raw_result = TCPScannerInstance.getResult()
        ip = device.ip_addr
        ports = []
        for entry in raw_result:
            _, port = entry
            ports.append(port)

        # store result to DB
        with model.write_lock:
            with model.db:
                
                    known_ports = eval(device.open_tcp_ports) # dont forget eval()

                    # 要比较一下旧和新是否有所不同，然后日志输出改的能看到旧和新
                    if known_ports == ports:
                        print(f"[TCP Scan] {ip}: Already have {known_ports}, No new ports found")
                        common.log(f"[TCP Scan] {ip}: Already have {known_ports}, No new ports found")
                    else:
                        merge_ports = list(set(known_ports + ports)) # add and remove repeating elements
                        device.open_tcp_ports = merge_ports
                        device.save()
                        print(f"[TCP Scan] {ip}: Already have {known_ports}, this round found {ports}")
                        common.log(f"[TCP Scan] {ip}: Already have {known_ports}, this round found {ports}")

        TCPScannerInstance.clearResult() # prepare for next one

    # free memory
    del TCPScannerInstance

    print("[TCP Scan] Exit")
