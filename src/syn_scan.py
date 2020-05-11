"""
Continuously sends out SYN packets.

"""
import scapy.all as sc
import threading
import utils
import time
import itertools
import random
from host_state import HostState
from parse_available_ports import get_port_list


# pylint: disable=no-member


SYN_SCAN_SOURCE_PORT = 44444
SYN_SCAN_SEQ_NUM = 44444


class SynScan(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)
        self._host_state = host_state

        self._lock = threading.Lock()
        self._active = False

        self._thread = threading.Thread(target=self._syn_scan_thread)
        self._thread.daemon = True

    def start(self):

        with self._lock:
            self._active = True

        utils.log('[SYN Scanning] Starting.')
        self._thread.start()

    def _syn_scan_thread(self):

        utils.restart_upon_crash(self._syn_scan_thread_helper)

    def _syn_scan_thread_helper(self):

        while True:

            time.sleep(1)

            if not self._host_state.is_inspecting():
                continue

            # Build a random list of (ip, port).
            port_list = get_port_list()
            ip_list = self._host_state.ip_mac_dict.keys()
            ip_port_list = list(itertools.product(ip_list, port_list))
            random.shuffle(ip_port_list)

            if len(ip_list) == 0:
                continue

            utils.log('[SYN Scanning] Start scanning {} ports over IPs: {}'.format(
                len(port_list),
                ', '.join(ip_list)
            ))

            for (ip, port) in ip_port_list:

                time.sleep(0.01)

                syn_pkt = sc.IP(dst=ip) / \
                    sc.TCP(dport=port, sport=SYN_SCAN_SOURCE_PORT, flags="S", seq=SYN_SCAN_SEQ_NUM)
                sc.send(syn_pkt, verbose=0)

                with self._lock:
                    if not self._active:
                        return

    def stop(self):

        with self._lock:
            self._active = False

        self._thread.join()

        utils.log('[SYN Scanning] Stopped.')
