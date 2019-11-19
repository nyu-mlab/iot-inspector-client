"""
Thread that continuously captures and processes packets.

"""
import scapy.all as sc
import threading
import utils
from host_state import HostState
import time


class PacketCapture(object):

    def __init__(self, host_state):

        assert isinstance(host_state, HostState)
        self._host_state = host_state

        self._lock = threading.Lock()
        self._active = True

        self._thread = threading.Thread(target=self._capture_packets)
        self._thread.daemon = True

    def start(self):

        with self._lock:
            self._active = True

        utils.log('[Packet Capture] Starting.')
        self._thread.start()

    def _capture_packets(self):

        while self._is_active():
            if not self._host_state.is_inspecting():
                time.sleep(2)
                continue

            result = utils.safe_run(sc.sniff, kwargs={
                'prn': self._host_state.packet_processor.process_packet,
                'stop_filter':
                    lambda _:
                        not self._is_active() or
                        not self._host_state.is_inspecting(),
                'filter': 'arp' +
                    ' or (host not {} and ether host {})'.format(
                        self._host_state.host_ip,
                        self._host_state.host_mac) +
                    ' or (port 67 or port 68)',
                'timeout': 30
            })

            if isinstance(result, utils._SafeRunError):
                time.sleep(1)

    def _is_active(self):

        with self._lock:
            return self._active

    def stop(self):

        utils.log('[Packet Capture] Stopping.')

        with self._lock:
            self._active = False

        self._thread.join()

        utils.log('[Packet Capture] Stopped.')
