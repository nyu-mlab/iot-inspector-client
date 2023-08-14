"""
Functions for processing the TLS layer in packets.

This module is in a separate file because I don't want `from scapy.all import *` (required for `TLSClientHello`) to pollute the namespace.

"""
from scapy.all import *


def extract_sni(packet) -> str:
    """
    Returns the SNI of a packet.

    """
    try:
        tls_layer = packet[TLSClientHello] # type: ignore
    except IndexError:
        return ''

    for attr in ['ext', 'extensions']:
        extensions = getattr(tls_layer, attr, [])
        if extensions:
            for extension in extensions:
                try:
                    if extension.type == 0:
                        return extension.servernames[0].servername.decode()
                except Exception:
                    pass

    return ''

