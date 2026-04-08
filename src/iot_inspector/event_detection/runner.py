"""Offline inference pipeline that reuses event_detection components."""

from __future__ import annotations

import argparse
import ipaddress
import logging
import os
from dataclasses import dataclass
from typing import List, Tuple

from scapy.all import PcapReader
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import Ether
from scapy.layers.tls.all import TLS
from iot_inspector.event_detection import utils, feature_standardization, model_selection, predict_event, global_state
from iot_inspector.event_detection import burst_processor, feature_generation, packet_processor, periodic_filter


logger = logging.getLogger(__name__)


BurstTuple = Tuple[tuple, float, list]


@dataclass
class InferenceStats:
    def __init__(self):
        pass

    packets_seen: int = 0
    packets_filtered: int = 0
    bursts_emitted: int = 0
    events_emitted: int = 0


class OfflineBurstAssembler:
    """Assemble bursts offline without relying on live Inspector state."""

    def __init__(self, device_mac: str, burst_interval: float):
        self.device_mac = device_mac.lower() if device_mac else None
        self.burst_interval = burst_interval
        self.burst_dict_start_time: dict[tuple, float] = {}
        self.burst_dict_all_burst: dict[tuple, list] = {}

    def _hostnames_from_packet(self, pkt) -> tuple[str, str]:
        src_ip_addr = pkt[IP].src
        dst_ip_addr = pkt[IP].dst
        src_hostname = utils.get_hostname_from_ip_addr(src_ip_addr)
        dst_hostname = utils.get_hostname_from_ip_addr(dst_ip_addr)

        if src_hostname == "":
            try:
                src_hostname = pkt[TLS].server_name.decode("utf-8")
            except (AttributeError, UnicodeDecodeError):
                src_hostname = ""

        if dst_hostname == "":
            try:
                dst_hostname = pkt[TLS].server_name.decode("utf-8")
            except (AttributeError, UnicodeDecodeError):
                dst_hostname = ""

        return src_hostname, dst_hostname

    def process_packet(self, pkt) -> List[BurstTuple]:
        if TCP in pkt:
            protocol = "TCP"
            layer = TCP
        elif UDP in pkt:
            protocol = "UDP"
            layer = UDP
        else:
            return []

        if not (Ether in pkt and IP in pkt):
            return []

        src_mac_addr = pkt[Ether].src
        dst_mac_addr = pkt[Ether].dst
        src_mac_lower = src_mac_addr.lower()
        dst_mac_lower = dst_mac_addr.lower()

        if self.device_mac and self.device_mac not in (src_mac_lower, dst_mac_lower):
            return []

        src_ip_addr = pkt[IP].src
        dst_ip_addr = pkt[IP].dst

        if dst_mac_addr == "ff:ff:ff:ff:ff:ff" or dst_ip_addr == "255.255.255.255":
            return []

        if not utils.validate_ip_address(src_ip_addr) or not utils.validate_ip_address(dst_ip_addr):
            return []

        time_epoch = float(pkt.time)
        frame_len = len(pkt)
        ip_proto = pkt[IP].proto

        try:
            highest_layer = pkt.lastlayer()
            ws_protocol = getattr(highest_layer, "name", str(highest_layer))
        except Exception:
            ws_protocol = protocol

        src_hostname, dst_hostname = self._hostnames_from_packet(pkt)

        if self.device_mac:
            if src_mac_lower == self.device_mac:
                flow_key = (ip_proto, src_ip_addr, pkt[layer].sport, dst_ip_addr, pkt[layer].dport, src_mac_addr)
                hostname = dst_hostname.lower()
            else:
                flow_key = (ip_proto, dst_ip_addr, pkt[layer].dport, src_ip_addr, pkt[layer].sport, dst_mac_addr)
                hostname = src_hostname.lower()
        else:
            flow_key = (ip_proto, src_ip_addr, pkt[layer].sport, dst_ip_addr, pkt[layer].dport, src_mac_addr)
            hostname = dst_hostname.lower()

            if dst_hostname == "(local network)" and src_hostname != "(local network)":
                flow_key = (ip_proto, dst_ip_addr, pkt[layer].dport, src_ip_addr, pkt[layer].sport, dst_mac_addr)
                hostname = src_hostname.lower()
            elif dst_hostname == "(local network)" and src_hostname == "(local network)":
                if int(ipaddress.ip_address(dst_ip_addr)) > int(ipaddress.ip_address(src_ip_addr)):
                    flow_key = (ip_proto, dst_ip_addr, pkt[layer].dport, src_ip_addr, pkt[layer].sport, dst_mac_addr)
                    hostname = src_hostname.lower()

        burst_start_time = self.burst_dict_start_time.setdefault(flow_key, time_epoch)
        completed: List[BurstTuple] = []

        if (time_epoch - burst_start_time) > self.burst_interval:
            pop_time = self.burst_dict_start_time.pop(flow_key, 0)
            pop_burst = self.burst_dict_all_burst.pop((flow_key, burst_start_time), [])
            if pop_burst:
                completed.append((flow_key, pop_time, pop_burst))

        self.burst_dict_all_burst.setdefault((flow_key, burst_start_time), []).append(
            [
                time_epoch,
                frame_len,
                ws_protocol,
                hostname,
                ip_proto,
                src_ip_addr,
                pkt[layer].sport,
                dst_ip_addr,
                pkt[layer].dport,
                dst_mac_addr,
            ]
        )

        for key in list(self.burst_dict_all_burst):
            if (time_epoch - key[1]) > self.burst_interval:
                pop_time = self.burst_dict_start_time.pop(key[0], 0)
                pop_burst = self.burst_dict_all_burst.pop((key[0], key[1]), [])
                if pop_burst:
                    completed.append((key[0], pop_time, pop_burst))

        return completed

    def flush(self) -> List[BurstTuple]:
        completed: List[BurstTuple] = []
        for key, pop_burst in list(self.burst_dict_all_burst.items()):
            flow_key, pop_time = key
            if pop_burst:
                completed.append((flow_key, pop_time, pop_burst))
            self.burst_dict_all_burst.pop(key, None)
            self.burst_dict_start_time.pop(flow_key, None)
        return completed


def _drain_queue(queue_obj) -> list:
    items = []
    while True:
        try:
            items.append(queue_obj.get_nowait())
        except Exception:
            break
    return items


def _run_inference(flow_key, pop_time, pop_burst) -> None:
    burst_features = feature_generation.compute_burst_features(flow_key, pop_time, pop_burst)
    if burst_features is None:
        return

    standardized = feature_standardization.standardize_burst_feature_data(burst_features)
    if standardized is None:
        return

    filtered = periodic_filter.filter_periodic_burst(*standardized)
    if filtered is None:
        return

    burst, device_name, model_name = filtered
    predict_event.predict_event_helper(burst, device_name, model_name)


def _resolve_model_name(device_name: str, model_name: str) -> str:
    if model_name:
        return model_name
    if device_name:
        _, best_match = model_selection.find_best_match(device_name)
        return best_match
    return "unknown"


def run_offline_inference(
    pcap_path: str,
    device_mac: str,
    device_name: str,
    model_name: str,
    max_packets: int = None) -> tuple[List[tuple], InferenceStats]:
    if not os.path.exists(pcap_path):
        raise FileNotFoundError(pcap_path)

    stats = InferenceStats()
    packet_processor.seen_packets = set()
    _drain_queue(global_state.filtered_event_queue)

    resolved_model = _resolve_model_name(device_name, model_name)
    feature_standardization.get_product_name_by_mac = lambda _mac: resolved_model

    assembler = OfflineBurstAssembler(
        device_mac=device_mac,
        burst_interval=burst_processor.BURST_WRITE_INTERVAL,
    )

    with PcapReader(pcap_path) as reader:
        for pkt in reader:
            stats.packets_seen += 1
            if max_packets is not None and stats.packets_seen > max_packets:
                break

            filtered_pkt = packet_processor.filter_packet(pkt)
            if filtered_pkt is None:
                continue
            stats.packets_filtered += 1

            for flow_key, pop_time, pop_burst in assembler.process_packet(filtered_pkt):
                stats.bursts_emitted += 1
                _run_inference(flow_key, pop_time, pop_burst)

    for flow_key, pop_time, pop_burst in assembler.flush():
        stats.bursts_emitted += 1
        _run_inference(flow_key, pop_time, pop_burst)

    events = _drain_queue(global_state.filtered_event_queue)
    stats.events_emitted = len(events)
    return events, stats


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Offline event inference from a pcap file using event_detection pipeline.",
    )
    parser.add_argument("-p", "--pcap", dest="pcap", action="store",
                        type=str, required=True, help="Path to the pcap file to analyze.")
    parser.add_argument("-m", "--device-mac", dest="device_mac", action="store",
                        type=str, required=True, help="MAC address of the device that produced the capture.")

    # For the exact model name, see the './models/binary/rf/ and you put the folder name, e.g. 'echoshow5' or 'bulb`'
    parser.add_argument("--model-name", dest="model_name", action="store",
                        type=str, help="Exact model folder name to use for inference.")
    # The device name, you take a string, and you roughly try to match with a model name, e.g. if you provide 'amazon plug' it might infer' amazon-plug' model
    parser.add_argument("--device-name", dest="device_name", action="store",
                        type=str, help="Human-readable device name for model matching.")

    # Optional, you can put a limit on number of packets to analyze
    parser.add_argument("--max-packets", dest="max_packets", type=int,
                        help="Optional limit on number of packets to process.")
    parser.add_argument(
        "--log-level", "-l",
        default="INFO",
        type=str,
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )
    return parser


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    if not args.device_name and not args.model_name:
        parser.error("Provide --device-name or --model-name for model selection.")

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    # Assuming -p can now be a directory or a file
    input_path = args.pcap

    if os.path.isfile(input_path):
        packet_captures = [input_path]
    else:
        packet_captures = []
        for root, _, files in os.walk(input_path):
            for file in files:
                # Check for pcap or pcapng extensions
                if file.lower().endswith(('.pcap', '.pcapng')):
                    packet_captures.append(os.path.join(str(root), str(file)))

    if not packet_captures:
        print(f"No PCAP files found at {input_path}")
        return

    for pcap in packet_captures:
        logger.info(f"🚀 Processing: {pcap}")
        events, stats = run_offline_inference(
            pcap_path=pcap,
            device_mac=args.device_mac.lower(),
            device_name=args.device_name,
            model_name=args.model_name,
            max_packets=args.max_packets,
        )
        file_root, _ = os.path.splitext(pcap)
        output_file = f"{file_root}_offline_event_inference.txt"
        try:
            with open(output_file, "w") as fd:
                fd.write("--- Offline Event Inference Results ---\n")
                fd.write(f"Packets seen: {stats.packets_seen}\n")
                fd.write(f"Packets filtered: {stats.packets_filtered}\n")
                fd.write(f"Bursts processed: {stats.bursts_emitted}\n")
                fd.write(f"Events detected: {stats.events_emitted}\n")
                for device, ts, event in events:
                    fd.write(f"{device}\t{ts}\t{event}\n")
            logger.info(f"Successfully saved plot to '{output_file}'")
        except Exception as e:
            logger.error(f"Error saving plot to '{output_file}': {e}")


if __name__ == "__main__":
    main()
