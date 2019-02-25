"""
Based on ARP packets received, sends out spoofed ARP packets.

"""
from host_state import HostState
import scapy.all as sc
import threading
import utils
import time


# Min seconds between successive spoofed packets
MIN_ARP_SPOOF_INTERVAL = 0.01


class ArpSpoof(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)
        self._host_state = host_state

        self._lock = threading.Lock()
        self._active = True
        self._thread = threading.Thread(target=self._arp_spoof_loop)
        self._thread.daemon = True

    def start(self):

        with self._lock:
            self._active = True

        utils.log('[Arp Spoof] Starting.')
        self._thread.start()

    def _arp_spoof_loop(self):

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

            utils.log('[ARP Spoof] Cache:', ip_mac_dict)
            utils.log(
                '[ARP Spoof] Whitelist:', self._host_state.device_whitelist
            )

            # Get gateway MAC addr
            try:
                gateway_mac = ip_mac_dict[gateway_ip]
            except KeyError:
                continue

            # Spoof individual devices on the network.
            for (victim_ip, victim_mac) in ip_mac_dict.items():

                if victim_ip == gateway_ip:
                    continue

                # Check against whitelist.
                victim_device_id = \
                    utils.get_device_id(victim_mac, self._host_state)
                if victim_device_id not in self._host_state.device_whitelist:
                    if not utils.LOCAL_TEST_MODE:
                        utils.log('[ARP Spoof] Ignore:', victim_ip, victim_mac)
                        continue

                if utils.TEST_OUI_LIST:
                    victim_mac_oui = utils.get_oui(victim_mac)
                    if victim_mac_oui not in utils.TEST_OUI_LIST:
                        continue

                utils.safe_run(
                    self._arp_spoof,
                    args=(victim_mac, victim_ip, gateway_mac, gateway_ip)
                )

                with self._lock:
                    if not self._active:
                        return

                time.sleep(max(MIN_ARP_SPOOF_INTERVAL, 2.0 / len(ip_mac_dict)))

    def _arp_spoof(self, victim_mac, victim_ip, gateway_mac, gateway_ip):
        """Sends out spoofed packets for a single target."""

        gateway_arp = sc.ARP()
        gateway_arp.op = 2
        gateway_arp.psrc = victim_ip
        gateway_arp.hwdst = gateway_mac
        gateway_arp.pdst = gateway_ip

        victim_arp = sc.ARP()
        victim_arp.op = 2
        victim_arp.psrc = gateway_ip
        victim_arp.hwdst = victim_mac
        victim_arp.pdst = victim_ip

        sc.send(victim_arp, verbose=0)
        sc.send(gateway_arp, verbose=0)

    def stop(self):

        utils.log('[Arp Spoof] Stopping.')

        with self._lock:
            self._active = False

        self._thread.join()

        utils.log('[Arp Spoof] Stopped.')
