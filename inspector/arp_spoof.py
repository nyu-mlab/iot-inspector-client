"""
Based on ARP packets received, sends out spoofed ARP packets.

"""
import scapy.all as sc
import concurrent.futures
import multiprocessing
import threading
import time

from host_state import HostState
import utils
import sys
import asyncio

import logging
import os


# Min seconds between successive spoofed packets
MIN_ARP_SPOOF_INTERVAL = 0.01

LOG_FORMAT_STRING = '%(asctime)s %(levelname)-8s %(filename)s %(lineno)d %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT_STRING, datefmt=LOG_DATEFMT,
                                        filename=os.path.splitext(os.path.basename(__file__))[0] + ".log", filemode="w")
logger = logging.getLogger(__name__)


class ArpSpoof(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)
        self._host_state = host_state

        self._lock = threading.Lock()
        self._active = True
        #self._thread = threading.Thread(target=self._arp_spoof_loop)
        self._thread = threading.Thread(target=self._arp_spoof_loop_async_wrapper)
        self._thread.daemon = True

    def start(self):

        with self._lock:
            self._active = True

        utils.log('[Arp Spoof] Starting.')
        self._thread.start()

    def _arp_spoof_loop(self):

        prev_ip_mac_dict = None

        while True:

            if not self._host_state.is_inspecting():
                time.sleep(2)
                continue

            time.sleep(1)

            with self._lock:
                if not self._active:
                    return

            with self._host_state.lock:
                if not self._host_state.has_consent:
                    utils.log('[ARP Spoof] No consent; no spoofing.')
                    continue

            # Get ARP cache
            ip_mac_dict = self._host_state.get_ip_mac_dict_copy()
            gateway_ip = self._host_state.gateway_ip
            # print('Discovered devices:', len(ip_mac_dict))
            if str(ip_mac_dict) != str(prev_ip_mac_dict):
                prev_ip_mac_dict = ip_mac_dict

            utils.log('[ARP Spoof] Cache: {} devices, {}'.format(len(ip_mac_dict), ip_mac_dict))
            len_of_whitelist = len(self._host_state.device_whitelist)
            utils.log(
                '[ARP Spoof] Whitelist:{} devices, {}'.format(len_of_whitelist, self._host_state.device_whitelist)
            )
            
            # Get gateway MAC addr
            try:
                gateway_mac = ip_mac_dict[gateway_ip]
            except KeyError:
                continue

            whitelist_ip_mac = []

            # Add gateway
            whitelist_ip_mac.append((gateway_ip, gateway_mac))

            # Build device-to-device whitelist
            for ip, mac in ip_mac_dict.items():
                device_id = utils.get_device_id(mac, self._host_state)
                if device_id not in self._host_state.device_whitelist:
                    utils.log('[ARP Spoof] Ignore:', ip, mac)
                    continue
                whitelist_ip_mac.append((ip, mac))
            
            # print('Spoof devices:', whitelist_ip_mac)

            # Spoof individual devices on the network.
            for (victim_ip, victim_mac) in ip_mac_dict.items():

                if victim_ip == gateway_ip:
                    continue

                # Check against whitelist.
                victim_device_id = \
                    utils.get_device_id(victim_mac, self._host_state)
                if victim_device_id not in self._host_state.device_whitelist:
                    utils.log('[ARP Spoof] Ignore:', victim_ip, victim_mac)
                    continue

                if utils.TEST_OUI_LIST:
                    victim_mac_oui = utils.get_oui(victim_mac)
                    if victim_mac_oui not in utils.TEST_OUI_LIST:
                        continue

                utils.safe_run(
                    self._arp_spoof,
                    args=(victim_mac, victim_ip, whitelist_ip_mac)
                )

                with self._lock:
                    if not self._active:
                        return

                time.sleep(max(MIN_ARP_SPOOF_INTERVAL, 2.0 / len(ip_mac_dict)))

    def _arp_spoof(self, victim_mac, victim_ip, whitelist_ip_mac):
        """Sends out spoofed packets for a single target."""

        with self._host_state.lock:
            spoof_arp = self._host_state.spoof_arp
            host_mac = self._host_state.host_mac

        for dest_ip, dest_mac in whitelist_ip_mac:

            if victim_ip == dest_ip:
                continue
            # send ARP spoof request to destination 
            # victim -> host -> destination
            dest_arp = sc.ARP()
            dest_arp.op = 1
            dest_arp.psrc = victim_ip
            dest_arp.hwsrc = host_mac
            dest_arp.hwdst = dest_mac
            dest_arp.pdst = dest_ip
            if not spoof_arp:
                dest_arp.hwsrc = victim_mac
                utils.log('[Arp Spoof] Restoring', victim_ip, '->', dest_ip)
            # send ARP spoof request to victim
            # destination -> host -> victim
            victim_arp = sc.ARP()
            victim_arp.op = 1
            victim_arp.psrc = dest_ip
            victim_arp.hwsrc = host_mac
            victim_arp.hwdst = victim_mac
            victim_arp.pdst = victim_ip
            if not spoof_arp:
                victim_arp.hwsrc = dest_mac
                utils.log('[Arp Spoof] Restoring', dest_ip, '->', victim_ip)

            sc.send(victim_arp, iface=sc.conf.iface, verbose=0)
            sc.send(dest_arp, iface=sc.conf.iface, verbose=0)

    def _arp_spoof_loop_async_wrapper(self):
        prev_ip_mac_dict = None
        while True:
            if not self._host_state.is_inspecting():
                time.sleep(2)
                continue
            time.sleep(1)
            with self._lock:
                if not self._active:
                    return
            with self._host_state.lock:
                if not self._host_state.has_consent:
                    utils.log('[ARP Spoof] No consent; no spoofing.')
                    continue
            # Get ARP cache
            ip_mac_dict = self._host_state.get_ip_mac_dict_copy()
            gateway_ip = self._host_state.gateway_ip
            logger.info(f'# of discovered devices :{len(ip_mac_dict)}')
            if str(ip_mac_dict) != str(prev_ip_mac_dict):
                prev_ip_mac_dict = ip_mac_dict
            utils.log('[ARP Spoof] Cache: {} devices, {}'.format(len(ip_mac_dict), ip_mac_dict))
            len_of_whitelist = len(self._host_state.device_whitelist)
            utils.log(
                '[ARP Spoof] Whitelist:{} devices, {}'.format(len_of_whitelist, self._host_state.device_whitelist)
            )
            # Get gateway MAC addr
            try:
                gateway_mac = ip_mac_dict[gateway_ip]
            except KeyError:
                continue
            whitelist_ip_mac = []
            # Add gateway
            whitelist_ip_mac.append((gateway_ip, gateway_mac))
            # Build device-to-device whitelist
            for ip, mac in ip_mac_dict.items():
                device_id = utils.get_device_id(mac, self._host_state)
                if device_id not in self._host_state.device_whitelist:
                    utils.log('[ARP Spoof] Ignore:', ip, mac)
                    logger.info(f'[ARP] igonore the device {ip}, {mac}')
                    continue
                whitelist_ip_mac.append((ip, mac))
            logger.info(f"Allowed list: {whitelist_ip_mac}")
            logger.info(f"Target list: {ip_mac_dict}")
            # Spoof individual devices on the network.
            # For now we are using multiprocessing because it's faster
            # multi-processing takes ~5-6 secs and multi-threading takes ~11-12 secs to spoof all the devices
            self._arp_spoof_loop_multiprocessing(whitelist_ip_mac)
            #self._arp_spoof_loop_multithreaded(whitelist_ip_mac)
            '''
            or it could be made async if this method is declared async 
            and _arp_spoof_loop, and _arp_spoof is made async. 
            We would have to call async version _arp_spoof with asyncio.to_thread(_arp_spoof_async)
            '''

    def _arp_spoof_loop_multithreaded(self, whitelist_ip_mac):
        # Spoof individual devices on the network.
        logger.info('Start of spoofing loop...')
        params_victim_ip = list()
        params_victim_mac = list()
        params_whitelist = list()
        for (victim_ip, victim_mac) in whitelist_ip_mac:
            logger.info(f'Begin inside loop: {victim_ip}, {victim_mac}')
            if utils.TEST_OUI_LIST:
                victim_mac_oui = utils.get_oui(victim_mac)
                if victim_mac_oui not in utils.TEST_OUI_LIST:
                    continue
            params_victim_ip.append(victim_ip)
            params_victim_mac.append(victim_mac)
            params_whitelist.append(whitelist_ip_mac)
            with self._lock:
                if not self._active:
                    return
            logger.info(f'End inside loop.')
        try:
            # Threading takes ~11/12 seconds per loop
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(self._arp_spoof_multithreaded, params_victim_mac, params_victim_ip, params_whitelist)
        except KeyboardInterrupt:
            logger.info("Caught Keyboard interrupt. Going to stop spoofing now...")
            self._host_state.spoof_arp = False
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(self._arp_spoof_multithreaded, params_victim_mac, params_victim_ip, params_whitelist)                
            logger.info("MAC addresses are restored!")
        finally:
            logger.info("Done in this loop")
        time.sleep(1)

    def _arp_spoof_multithreaded(self, victim_mac, victim_ip, whitelist_ip_mac):
        try:
            """Sends out spoofed packets for a single target."""
            with self._host_state.lock:
                spoof_arp = self._host_state.spoof_arp
                host_mac = self._host_state.host_mac
            if spoof_arp:
                logger.info(f"Poisioning ARP caches of {whitelist_ip_mac} for {victim_ip}: {victim_mac}")
            else:
                logger.info(f"Restoreing ARP caches of {whitelist_ip_mac} for {victim_ip}: {victim_mac}")    
            pkt_list = list()
            for dest_ip, dest_mac in whitelist_ip_mac:
                if victim_ip == dest_ip:
                    continue
                victim_arp = sc.Ether(dst=victim_mac)/sc.ARP(op="is-at",
                            pdst=victim_ip, hwdst=victim_mac,
                            hwsrc=host_mac, psrc=dest_ip)            
                if not spoof_arp:
                    victim_arp.hwsrc = dest_mac
                    utils.log('[Arp Spoof] Restoring', dest_ip, '->', victim_ip)
                    logger.info(f"Packet for restoring the MAC of {dest_ip} with {dest_mac} has been created")
                pkt_list.append(victim_arp)
            sc.sendp(pkt_list)
        except KeyboardInterrupt:
            logger.info("KB interrupt")
            self._host_state.spoof_arp = False
            self._arp_spoof_multithreaded(victim_mac, victim_ip, whitelist_ip_mac)
        finally:
            logger.info(f"Exiting ARP spoofing of {victim_ip}")

    def _arp_spoof_loop_multiprocessing(self, whitelist_ip_mac):
        logger.info('Start of spoofing loop...')
        params = list()
        for (victim_ip, victim_mac) in whitelist_ip_mac:
            logger.info(f'Begin inside loop: {victim_ip}, {victim_mac}')
            if utils.TEST_OUI_LIST:
                victim_mac_oui = utils.get_oui(victim_mac)
                if victim_mac_oui not in utils.TEST_OUI_LIST:
                    continue
            params.append((self._host_state.host_mac, self._host_state.spoof_arp,
                                victim_mac, victim_ip, whitelist_ip_mac))
            with self._lock:
                if not self._active:
                    return
            logger.info(f'End inside loop.')
        try:
            # Multiprocessing takes max ~5-6 seconds
            # If processes is None then the number returned by os.cpu_count() is used
            with multiprocessing.Pool() as pool:
                pool.starmap(ArpSpoof._arp_spoof_static, params)
        except KeyboardInterrupt:
            logger.info("Caught Keyboard interrupt. Going to stop spoofing now...")               
            for i in range(len(whitelist_ip_mac.items())):
                params_i = params[i]
                params_i[1] = False
                params[i] = params_i
            with multiprocessing.Pool() as pool:
                pool.starmap(ArpSpoof._arp_spoof_static, params)
            logger.info("MAC addresses are restored!")
        finally:
            logger.info("Done in this loop")
        time.sleep(1)

    @staticmethod
    def _arp_spoof_static(host_mac, spoof_arp, victim_mac, victim_ip, whitelist_ip_mac):
        try:
            if spoof_arp:
                logger.info(f"Poisioning ARP caches of {whitelist_ip_mac} for {victim_ip}: {victim_mac}")
            else:
                logger.info(f"Restoreing ARP caches of {whitelist_ip_mac} for {victim_ip}: {victim_mac}")
            pkt_list = list()
            for dest_ip, dest_mac in whitelist_ip_mac:
                if victim_ip == dest_ip:
                    continue
                victim_arp_pkt = sc.Ether(dst=victim_mac)/sc.ARP(op="is-at", #op="who-has", 
                            pdst=victim_ip, hwdst=victim_mac,
                            hwsrc=host_mac, psrc=dest_ip)    
                if not spoof_arp:
                    victim_arp_pkt[sc.ARP].hwsrc = dest_mac
                    utils.log('[Arp Spoof] Restoring', dest_ip, '->', victim_ip)
                    logger.info(f"Packet for restoring the MAC of {dest_ip} with {dest_mac} has been created")
                pkt_list.append(victim_arp_pkt)
            logger.info(f"Number of packets being sent: {len(pkt_list)}")
            sc.sendp(pkt_list)
        except KeyboardInterrupt:
            logger.info("KB interrupt")
            ArpSpoof._arp_spoof_static(host_mac,False, victim_mac, victim_ip, whitelist_ip_mac)
        finally:
            logger.info(f"Exiting ARP spoofing of {victim_ip}")

    def stop(self):

        utils.log('[Arp Spoof] Stopping.')
        logger.info("Stopping ARP spoofing!")

        with self._lock:
            self._active = False

        self._thread.join()

        utils.log('[Arp Spoof] Stopped.')
