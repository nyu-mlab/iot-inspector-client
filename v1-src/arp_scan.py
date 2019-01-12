"""
Continuously sends out ARP discover packets.

"""
import scapy.all as sc
import threading
import utils
import time
from host_state import HostState


class ArpScan(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)

        self._lock = threading.Lock()
        self._active = True

        self._thread = threading.Thread(target=self._arp_scan_thread)
        self._thread.daemon = True

    def start(self):

        with self._lock:
            self._active = True

        utils.log('[ARP Scanning] Starting.')
        self._thread.start()

    def _arp_scan_thread(self):

        utils.restart_upon_crash(self._arp_scan_thread_helper)

    def _arp_scan_thread_helper(self):

        while True:

            for ip in utils.get_network_ip_range():

                time.sleep(0.05)

                arp_pkt = sc.Ether(dst="ff:ff:ff:ff:ff:ff") / \
                    sc.ARP(pdst=ip, hwdst="ff:ff:ff:ff:ff:ff")
                sc.sendp(arp_pkt, verbose=0)

                with self._lock:
                    if not self._active:
                        return

    def stop(self):

        utils.log('[ARP Scanning] Stopping.')

        with self._lock:
            self._active = False

        self._thread.join()

        utils.log('[ARP Scanning] Stopped.')

