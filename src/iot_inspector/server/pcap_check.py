from scapy.packet import Packet
from scapy.all import Ether, IP
from typing import List
import datetime


def convert_bytes_to_packet(raw_packets: list, capture_times: list) -> List[Packet]:
    """
    Saves a list of raw packet bytes to a pcap file.

    Args:
        raw_packets (list): List of bytes objects representing raw packets.
        capture_times (list): The epoch time of each packet when it was captured by IoT Inspector.
    """
    scapy_packets = []
    for i, pkt_bytes in enumerate(raw_packets):
        try:
            pkt = Ether(pkt_bytes)
            if pkt.__class__.__name__ == "Raw":
                print("Warning: Packet parsed as Raw, attempting IP encapsulation")
                pkt = Ether() / IP(pkt_bytes)
        except Exception:
            try:
                pkt = Ether() / IP(pkt_bytes)
            except Exception as e:
                # Fallback for truly corrupted data
                print(f"Skipping corrupted packet at index {i}: {e}")
                continue

        # CRITICAL STEP: Assign the supplied original capture time
        # This is guaranteed to be correct for ALL packets.
        if len(capture_times) == len(raw_packets):
            pkt.time = capture_times[i]
        scapy_packets.append(pkt)
    return scapy_packets


def identify_tls_application_data(pkt: Packet) -> bool:
    """
    Checks a Scapy packet for the Raw layer and identifies if the payload is
    likely TLS Application Data for TLS 1.2 or TLS 1.3 based on the header bytes.

    TLS Header Structure (first 3 bytes):
    - Byte 1: Content Type (0x17 for Application Data)
    - Byte 2/3: Protocol Version (Major/Minor)

    Args:
        pkt (Packet): The Scapy packet object.

    Returns:
        bool: if the packet contains TLS Application Data for TLS 1.2 or TLS 1.3, False otherwise.
    """
    if "Raw" in pkt and len(pkt["Raw"].load) >= 3:
        raw_load = pkt["Raw"].load

        # Check for Application Data Content Type (0x17)
        if raw_load.startswith(b'\x17'):
            # Check the Version (Major 0x03)
            if raw_load[1] == 0x03:
                minor_version = raw_load[2]

                # Minor version 0x03 -> TLS 1.2 (or a compatibility mode for 1.3)
                if minor_version == 0x03:
                    # We can't definitively separate 1.2 from 1.3 without full handshake analysis,
                    # but the header is the same for the most common case.
                    return True

                # Minor version 0x01 -> TLS 1.0 (sometimes used by 1.3 for compatibility)
                elif minor_version == 0x01:
                    return True

    return False


def check_for_application_data(scapy_packets: List[Packet]) -> bool:
    """
    Search all packets for encrypted TLS 1.2/1.3 Application Data payload.
    The index and packet details are printed for the first match found.
    The index would match the index on Wireshark.

    Args:
        scapy_packets (list): List of processed Scapy Packet objects.

    Returns:
        bool: True if at least one packet contains L7 payload data, False otherwise.
    """
    for i, pkt in enumerate(scapy_packets, start=1):
        if identify_tls_application_data(pkt):
            print(f"Packet {i}, TLS Application Data found")
            pkt.show()
            return True
    return False


def make_pcap_filename(start_time: int, end_time: int) -> str:
    """
    Generates a pcap filename using the machine's local timezone.
    The format is: 'Mon-DD-YYYY_HH-MM-SSAM/PM_TZ_DurationSeconds.pcap'
    """
    # 1. Convert epoch to an 'aware' datetime object in the local timezone
    # .fromtimestamp(start_time) converts the epoch to local wall time
    # .astimezone() ensures it's an 'aware' object so %Z (timezone name) works
    start_dt = datetime.datetime.fromtimestamp(start_time).astimezone()
    duration_seconds = end_time - start_time

    # 2. Format: Mon-DD-YYYY_HH-MM-SSAM/PM_TZ
    # We use dashes '-' instead of colons ':' to ensure the filename is
    # compatible with Windows and macOS file systems.
    safe_start = start_dt.strftime("%b-%d-%Y_%I-%M-%S%p_%Z")

    # 3. Generate the final filename
    return f"{safe_start}_{duration_seconds:.2f}s.pcap"
