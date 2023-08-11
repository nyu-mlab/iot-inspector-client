"""
Captures and analyzes packets from the network.

"""
import scapy.all as sc
import core.global_state as global_state
import core.common as common



WINDOWS_TEXT = r'\n' * 10 + """
==================================================
            IoT Inspector is running
==================================================

To quit IoT Inspector, simply close this window.


"""



def start_packet_collector():

    # Show the WINDOWS_TEXT if we are running on Windows
    if common.get_os() == 'windows':
        print(WINDOWS_TEXT)

    sc.load_layer('tls')

    # Continuously sniff packets for 30 second intervals
    sc.sniff(
        prn=add_packet_to_queue,
        iface=global_state.host_active_interface,
        stop_filter=lambda _: not global_state.is_running,
        filter=f'(not arp and host not {global_state.host_ip_addr}) or arp', # Avoid capturing packets to/from the host itself, except ARP, which we need for discovery -- this is for performance improvement
        timeout=30
    )


def add_packet_to_queue(pkt):
    """
    Adds a packet to the packet queue.

    """
    with global_state.global_state_lock:
        if not global_state.is_inspecting:
            return

    global_state.packet_queue.put(pkt)