import ipaddress
import subprocess
import logging

from libinspector import networking
from .ttl_cache import ttl_cache
import libinspector.global_state as libinspector_state


logger = logging.getLogger(__name__)

@ttl_cache(maxsize=8192, ttl=15)
def validate_ip_address(address):
    """ check if it's a valid ip address

    Args:
        address (string): ip address

    Returns:
        bool: true as valid 
    """
    try:
        ip = ipaddress.ip_address(address)
        # print("IP address {} is valid. The object returned is {}".format(address, ip))
        return True
    except ValueError:
        # print("IP address {} is not valid".format(address)) 
        return False


@ttl_cache(maxsize=8192, ttl=15)
def get_hostname_from_ip_addr(ip_addr: str) -> str:
    """
    Returns the hostname associated with an IP address.
    Returns an empty string if the hostname is not found.
    """
    if networking.is_private_ip_addr(ip_addr):
        return '(local network)'

    # Note: Jakaria added code block for multicast ip checking; consult Danny
    if ipaddress.ip_address(ip_addr).is_multicast:
        return '(multicast)'

    # Step 1: Ask the database
    try:
        conn, rw_lock = libinspector_state.db_conn_and_lock
        with rw_lock:
            cursor = conn.execute(
                "SELECT hostname FROM hostnames WHERE ip_address = ?",
                (ip_addr,)
            )
            row = cursor.fetchone()
            if row:
                if row[0].endswith('.'):
                    return row[0][:-1]
                return row[0]
    except Exception:
        print("Error in get_hostname_from_ip_addr()")
        pass

    # Note: Ask libinspector if they have plans to store the hostnames in the server
    # Note: if yes, then add a function to pull hostnames from the server

    # Step 2: Ask libinspector SNI Extractor in the main thread

    # Step 3: # Step 3: Use `dig -x ip_address` for reverse DNS lookup
    try:
        result = subprocess.run(
                ["dig", "-x", ip_addr, "+short"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        hostname = result.stdout.strip()
        if hostname:
            # Remove trailing dots
            if hostname.endswith('.'):
                return hostname[:-1]
            return hostname
    except Exception as e:
        logging.error(f"Error resolving hostname for {ip_addr}: {e}")

    return ''