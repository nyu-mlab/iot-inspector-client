import argparse
import logging
from scapy.all import rdpcap, wrpcap, Ether, UDP
from scapy.layers.inet import TCP

# Set up logging for informative output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Define the MAC address placeholder for anonymization
ANONYMIZED_MAC = "00:00:00:00:00:00"

# Define ports for filtering:
# DHCP: UDP ports 67 (server) and 68 (client)
# MDNS: UDP port 5353
# SSDP: UDP port 1900
PORTS_TO_DROP = {67, 68, 5353, 1900, 80}


def sanitize_pcap(input_file: str, output_file: str):
    """
    Reads a PCAP file, anonymizes MAC addresses, drops specific control protocol packets,
    and writes the filtered packets to a new file.
    """
    logger.info(f"Starting sanitization process for: {input_file}")

    try:
        # 1. Read all packets from the input file
        packets = rdpcap(input_file)
    except FileNotFoundError:
        logger.error(f"Error: Input file not found at '{input_file}'")
        return
    except Exception as e:
        logger.error(f"Error reading PCAP file: {e}")
        return

    total_packets = len(packets)
    kept_packets = []
    dropped_count = 0
    anonymized_count = 0

    logger.info(f"Read {total_packets} packets. Starting filtering and anonymization...")

    for packet in packets:
        # --- Filtering Logic (Dropping packets) ---
        should_drop = False

        # Check for protocols using specific UDP ports (DHCP, MDNS, SSDP)
        if UDP in packet:
            udp_layer = packet[UDP]
            if udp_layer.sport in PORTS_TO_DROP or udp_layer.dport in PORTS_TO_DROP:
                should_drop = True
                dropped_count += 1

        if TCP in packet:
            tcp_layer = packet[TCP]
            if tcp_layer.sport in PORTS_TO_DROP or tcp_layer.dport in PORTS_TO_DROP:
                should_drop = True
                dropped_count += 1

        # You could also check for specific layer names if they are reliably dissected:
        # e.g., if packet.haslayer('DHCP') or packet.haslayer('MDNS'):
        #     should_drop = True

        if should_drop:
            continue  # Skip to the next packet if it needs to be dropped

        # --- Anonymization Logic ---
        if Ether in packet:
            # Anonymize source and destination MAC addresses
            packet[Ether].src = ANONYMIZED_MAC
            packet[Ether].dst = ANONYMIZED_MAC
            anonymized_count += 1

        # Keep the modified packet
        kept_packets.append(packet)

    # 3. Write the modified packets to the new file
    wrpcap(output_file, kept_packets)

    logger.info("-" * 40)
    logger.info("Anonymization complete.")
    logger.info(f"Total packets processed: {total_packets}")
    logger.info(f"Packets anonymized (Ethernet layer present): {anonymized_count}")
    logger.info(f"Packets dropped (SSDP/MDNS/DHCP): {dropped_count}")
    logger.info(f"Packets saved to '{output_file}': {len(kept_packets)}")
    logger.info("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        description="Anonymize MACs and filter specific control packets (DHCP, SSDP, MDNS) from a PCAP file."
    )
    parser.add_argument(
        "-i", "--input",
        dest='input_file',
        action='store',
        type=str,
        help="The path to the input PCAP file."
    )
    parser.add_argument(
        "-o", "--output",
        dest='output',
        action='store',
        type=str,
        default="sanitized_output.pcap",
        help="The path to save the anonymized PCAP file (default: sanitized_output.pcap)."
    )
    args = parser.parse_args()
    sanitize_pcap(args.input_file, args.output)


if __name__ == "__main__":
    main()
