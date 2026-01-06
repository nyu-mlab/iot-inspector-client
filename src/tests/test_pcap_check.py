import unittest
import os
from typing import List
from scapy.utils import rdpcap
from scapy.packet import Packet
from iot_inspector.server.pcap_check import check_for_application_data, convert_bytes_to_packet


def read_packets_from_pcap(filename: str) -> List[Packet]:
    """
    Reads packets from a Wireshark/PCAP file and returns them as a list of Scapy Packet objects.

    Args:
        filename (str): Path to the input PCAP file.

    Returns:
        List[Packet]: A list of Scapy Packet objects. Returns an empty list on failure.
    """
    fixed_packets = []
    try:
        # 1. Use rdpcap to read all packets from the file. This handles the PCAP metadata (like timestamps).
        packets = rdpcap(filename)

        # 2. Iterate and re-process each packet's raw bytes to ensure L3 dissection
        for pkt in packets:
            fixed_pkt = convert_bytes_to_packet([pkt.original], [])
            fixed_packets.extend(fixed_pkt)
        return fixed_packets
    except FileNotFoundError:
        print(f"Error: PCAP file not found at {filename}")
        return []
    except Exception as e:
        print(f"Error reading PCAP file {filename}: {e}")
        return []


class TestPcapIntegrity(unittest.TestCase):

    def test_no_application_data(self):
        """
        Read PCAP file and confirm application data is found or not.
        """
        no_app_pcap = os.path.join(os.path.dirname(__file__), "data", "no_application_data.pcap")
        self.assertNotEqual(len(no_app_pcap), 0, "Test PCAP file path should not be empty.")
        packets = read_packets_from_pcap(no_app_pcap)
        self.assertFalse(check_for_application_data(packets), "This PCAP should not have application data.")

    def test_application_data(self):
        app_pcap = os.path.join(os.path.dirname(__file__), "data", "application_data.pcap")
        self.assertNotEqual(len(app_pcap), 0, "Test PCAP file path should not be empty.")
        packets = read_packets_from_pcap(app_pcap)
        self.assertTrue(check_for_application_data(packets), "Application data should be detected in the PCAP. Packet 23 says TLS v1.2 and Application Data on Wireshark.")
