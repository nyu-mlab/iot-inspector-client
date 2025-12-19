import argparse
import logging
import datetime
from scapy.all import rdpcap, Ether
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def analyze_traffic(input_file: str, output_file: str, interval_minutes: int, target_mac: str):
    """
    Reads a PCAP file, calculates upload/download traffic for a specific MAC address
    over time, and generates a plot.

    Args:
        input_file (str): Path to the input PCAP file.
        output_file (str): Path to save the output PNG plot.
        interval_minutes (int): Time interval (in minutes) for aggregation.
        target_mac (str): The MAC address of the device to analyze (e.g., 'aa:bb:cc:dd:ee:ff').
    """
    if not os.path.exists(input_file):
        logger.error(f"Error: Input file not found at '{input_file}'")
        return

    # Normalize the target MAC to lowercase for case-insensitive comparison
    normalized_target_mac = target_mac.lower()

    logger.info(f"Starting analysis for: {input_file}")
    logger.info(f"Target MAC for analysis: {target_mac}")
    logger.info(f"Aggregation interval: {interval_minutes} minute(s)")

    try:
        # 1. Read all packets from the input file
        packets = rdpcap(input_file)
    except Exception as e:
        logger.error(f"Error reading PCAP file: {e}")
        return

    total_packets = len(packets)
    if total_packets == 0:
        logger.warning("The PCAP file contains no packets. Exiting.")
        return

    logger.info(f"Read {total_packets} packets. Starting data processing...")

    # Data structure to hold (timestamp, upload_bytes, download_bytes) for aggregation
    data = []

    for packet in packets:
        # Get the timestamp in datetime format
        ts = datetime.datetime.fromtimestamp(float(packet.time))

        # We need the Ethernet layer for MACs and packet size
        if Ether in packet:
            src_mac = packet[Ether].src.lower()
            dst_mac = packet[Ether].dst.lower()

            # Use the full packet length (wire size)
            packet_size = len(packet)

            upload_bytes = 0
            download_bytes = 0

            if src_mac == normalized_target_mac:
                # Target is the source MAC (Upload traffic)
                upload_bytes = packet_size
            elif dst_mac == normalized_target_mac:
                # Target is the destination MAC (Download traffic)
                download_bytes = packet_size

            # Only record if the packet involved the target MAC
            if upload_bytes > 0 or download_bytes > 0:
                data.append({
                    'timestamp': ts,
                    'upload_bytes': upload_bytes,
                    'download_bytes': download_bytes
                })

    # --- 2. Aggregate Data into Time Bins using Pandas ---
    df = pd.DataFrame(data)

    if df.empty:
        logger.warning(f"No traffic found involving MAC address '{target_mac}' in the PCAP. Exiting.")
        return

    # Set timestamp as the index
    df = df.set_index('timestamp')

    # Resample and sum bytes based on the requested interval (e.g., '1Min' or '5Min')
    interval = f'{interval_minutes}Min'
    df_agg = df.resample(interval).sum()

    # Remove rows where all traffic is zero
    df_agg = df_agg[(df_agg['upload_bytes'] > 0) | (df_agg['download_bytes'] > 0)]

    # --- 3. Plotting ---
    logger.info("Generating plot...")

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 7))

    # Convert bytes to megabytes for plotting
    df_agg['upload_mb'] = df_agg['upload_bytes'] / (1024 * 1024)
    df_agg['download_mb'] = df_agg['download_bytes'] / (1024 * 1024)

    # Plot the two series
    df_agg['upload_mb'].plot(ax=ax, label='Upload Traffic (MB)', marker='.', linestyle='-', color='teal', linewidth=1.5)
    df_agg['download_mb'].plot(ax=ax, label='Download Traffic (MB)', marker='.', linestyle='-', color='firebrick',
                               linewidth=1.5)

    # Customizing the plot
    ax.set_title(f"Network Traffic Over Time for MAC: {target_mac}", fontsize=16)
    ax.set_xlabel(f"Time (Aggregated every {interval_minutes} minute(s))", fontsize=12)
    ax.set_ylabel("Data Transfer (Megabytes)", fontsize=12)
    ax.legend(loc='upper right', fontsize=10)

    # Format the x-axis to show HH:MM time, suitable for long captures
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()

    # 4. Save the figure
    try:
        fig.savefig(output_file)
        logger.info(f"Successfully saved plot to '{output_file}'")
    except Exception as e:
        logger.error(f"Error saving plot to '{output_file}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze PCAP file to plot upload and download traffic over time for a specific MAC address."
    )
    parser.add_argument(
        "-i", "--input",
        dest="input_file",
        action="store",
        type=str,
        help="The path to the input PCAP file.",
        required=True
    )
    parser.add_argument(
        "-m", "--target-mac",
        dest="target_mac",
        action="store",
        type=str,
        required=True,
        help="The MAC address of the device to analyze (e.g., 'aa:bb:cc:dd:ee:ff')."
    )
    parser.add_argument(
        "-o", "--output",
        dest="output",
        action="store",
        type=str,
        default="traffic_timeseries.png",
        help="The path to save the output plot PNG file (default: traffic_timeseries.png)."
    )
    parser.add_argument(
        "--interval",
        dest="interval",
        action="store",
        type=int,
        default=1,
        help="The time aggregation interval in minutes (default: 1)."
    )

    args = parser.parse_args()
    analyze_traffic(args.input_file, args.output, args.interval, args.target_mac)