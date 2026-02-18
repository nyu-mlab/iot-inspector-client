import argparse
import logging
import datetime
from scapy.all import rdpcap, Ether
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def bin_traffic(df: pd.DataFrame, bin_size: float) -> tuple:
    """
    This function converts a pandas DataFrame that contains per-packet
    upload/download byte counts and relative timestamps into fixed-width
    time bins. It returns the array of bin edges and two arrays containing
    the total upload and download bytes accumulated for each bin.

    Args:
        df (pd.DataFrame): Input DataFrame which must contain the following
            columns (either as regular columns or available via the index):
                - rel_time (float): Seconds since the start of the capture.
                - upload_bytes (int/float): Bytes contributed as upload for
                  the packet/row.
                - download_bytes (int/float): Bytes contributed as download
                  for the packet/row.
            The DataFrame may include other columns; they will be ignored.
        bin_size (float): Width of each time bin in seconds. Must be > 0.

    Returns:
        tuple: (bins, upload_binned, download_binned)
            - bins (np.ndarray): 1-D array of bin edges generated with
              ``np.arange(0, max_rel_time + bin_size, bin_size)``. Length N.
            - upload_binned (np.ndarray): 1-D array of length N with the
              total upload bytes for each corresponding bin.
            - download_binned (np.ndarray): 1-D array of length N with the
              total download bytes for each corresponding bin.

    Notes:
        - Bins are created from 0 up to the maximum observed ``rel_time``
          (inclusive) with step ``bin_size``.
        - Mapping of times to bins uses ``numpy.digitize``'s default
          behaviour (``right=False``): an index i is returned such that
          ``bins[i-1] < x <= bins[i]``. Values less than or equal to the
          first bin edge (i.e. ``x <= bins[0]``) receive index 0 and are
          therefore ignored by this implementation. As a result, rows with
          ``rel_time == 0`` will not be counted.
        - If ``df`` is empty, the function returns three empty numpy arrays.

    Raises:
        ValueError: If ``bin_size`` is not a positive number (<= 0).

    Examples:
        >>> # df must contain rel_time, upload_bytes and download_bytes
        >>> bins, up, down = bin_traffic(df, 0.05)

    Performance:
        - Time complexity is O(n) in the number of rows in ``df``.
        - Memory usage is proportional to the number of bins (``max_rel_time / bin_size``).
    """
    # Validate input
    if bin_size <= 0:
        raise ValueError("bin_size must be a positive number")

    if df.empty:
        return np.array([]), np.array([]), np.array([])

    max_time = df['rel_time'].max()
    bins = np.arange(0, max_time + bin_size, bin_size)

    digitized = np.digitize(df['rel_time'], bins)

    upload_binned = np.zeros(len(bins))
    download_binned = np.zeros(len(bins))

    # Use numpy arrays for column access to avoid namedtuple attribute lookups
    upload_arr = df['upload_bytes'].to_numpy()
    download_arr = df['download_bytes'].to_numpy()

    for idx, up_bytes, down_bytes in zip(digitized, upload_arr, download_arr):
        bin_index = idx - 1
        if 0 <= bin_index < len(upload_binned):
            upload_binned[bin_index] += up_bytes
            download_binned[bin_index] += down_bytes
    return bins, upload_binned, download_binned


def analyze_traffic(input_file: str, output_file: str, target_mac: str, bin_size: float):
    """
    Reads a PCAP file, calculates upload/download traffic for a specific MAC address
    over time, and generates a plot.

    Args:
        input_file (str): Path to the input PCAP file.
        output_file (str): Path to save the output PNG plot.
        target_mac (str): The MAC address of the device to analyze (e.g., 'aa:bb:cc:dd:ee:ff').
        bin_size (float): Width of time bins in seconds for aggregating traffic data.
    """
    if not os.path.exists(input_file) or not os.path.isfile(input_file):
        logger.error(f"Error: Input file not found at '{input_file}'")
        return

    # Normalize the target MAC to lowercase for case-insensitive comparison
    normalized_target_mac = target_mac.lower()

    logger.info(f"Starting analysis for: {input_file}")
    logger.info(f"Target MAC for analysis: {target_mac}")
    logger.info(f"Time bin size: {bin_size} seconds")

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
    
    # Add relative time column (seconds since first packet)
    df['rel_time'] = (df.index - df.index.min()).total_seconds()
    bins, upload_binned, download_binned = bin_traffic(df, bin_size)

    # --- 3. Plotting ---
    logger.info("Generating plot...")

    plt.style.use('seaborn-v0_8-whitegrid')

    upload_mb = upload_binned / (1024 * 1024)
    download_mb = download_binned / (1024 * 1024)
    
    fig, axes = plt.subplots(
        nrows=2,
        ncols=1,
        figsize=(15, 8),
        sharex=True
    )
    
    axes[0].plot(bins, upload_mb, linewidth=1.0)
    axes[0].set_title(f"Upload Traffic (MAC: {target_mac})")
    axes[0].set_ylabel("MB per bin")
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(bins, download_mb, linewidth=1.0)
    axes[1].set_title("Download Traffic")
    axes[1].set_ylabel("MB per bin")
    axes[1].set_xlabel("Time (seconds since capture start)")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()

    # 4. Save the figure
    try:
        fig.savefig(output_file)
        logger.info(f"Successfully saved plot to '{output_file}'")
    except Exception as e:
        logger.error(f"Error saving plot to '{output_file}': {e}")


def main():
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
        "-b", "--bin",
        dest="bin_size",
        action="store",
        type=float,
        default=0.05,
        help="The width of time bins in seconds for aggregating traffic data (default: 0.05 seconds)."
    )
    args = parser.parse_args()
    analyze_traffic(args.input_file, args.output, args.target_mac, args.bin_size)


if __name__ == "__main__":
    main()
