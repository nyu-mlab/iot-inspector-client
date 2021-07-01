"""
Continuously sends out ARP discover packets.

"""
import scapy.all as sc
import threading
import time

from host_state import HostState
import utils


# pylint: disable=no-member


FAST_SCAN_SLEEP_TIME = 0.1
SLOW_SCAN_SLEEP_TIME = 0.5


class ArpScan(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)
        self._host_state = host_state

        self._lock = threading.Lock()
        self._active = False

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

        fast_scan_start_ts = None

        while True:

            if not self._host_state.is_inspecting():
                time.sleep(1)
                continue

            for ip in utils.get_network_ip_range():

                sleep_time = SLOW_SCAN_SLEEP_TIME

                # Whether we should scan fast or slow
                with self._host_state.lock:
                    fast_arp_scan = self._host_state.fast_arp_scan

                # If fast scan, we do it for at most 5 mins
                if fast_arp_scan:
                    sleep_time = FAST_SCAN_SLEEP_TIME
                    if fast_scan_start_ts is None:
                        fast_scan_start_ts = time.time()
                    else:
                        if time.time() - fast_scan_start_ts > 300:
                            fast_scan_start_ts = None
                            sleep_time = SLOW_SCAN_SLEEP_TIME
                            with self._host_state.lock:
                                self._host_state.fast_arp_scan = False

                time.sleep(sleep_time)

                arp_pkt = sc.Ether(dst="ff:ff:ff:ff:ff:ff") / \
                    sc.ARP(pdst=ip, hwdst="ff:ff:ff:ff:ff:ff")
                sc.sendp(arp_pkt, verbose=0)

                with self._lock:
                    if not self._active:
                        return

    def stop(self):

        with self._lock:
            self._active = False

        self._thread.join()

        utils.log('[ARP Scanning] Stopped.')
