import ipaddress
import socket
import logging

from libinspector import networking
from .ttl_cache import ttl_cache
import libinspector.global_state as libinspector_state
import common
from .model_selection import find_best_match


logger = logging.getLogger(__name__)

@ttl_cache(maxsize=8192, ttl=15)
def validate_ip_address(address: str) -> bool:
    """ check if it's a valid ip address

    Args:
        address (string): ip address

    Returns:
        bool: true as valid 
    """
    try:
        ipaddress.ip_address(address)
        # print("IP address {} is valid. The object returned is {}".format(address, ip))
        return True
    except ValueError:
        # print("IP address {} is not valid".format(address)) 
        return False


# Returns a list of all mac_address values from the devices table.

@ttl_cache(ttl=30)
def get_mac_address_list() -> list:
    """
    Returns a list of all mac_address values from the devices table.
    Assumes the table 'devices' exists and conn is a valid DB connection.
    """
    try:
        db_conn_and_lock = libinspector_state.db_conn_and_lock
        if db_conn_and_lock is None:
            return []
        conn, rw_lock = db_conn_and_lock
        with rw_lock:
            cursor = conn.execute("SELECT mac_address FROM devices")
            macs = [row[0] for row in cursor.fetchall()]
            return macs
    except Exception:
        logger.error("Error in get_hostname_from_ip_addr()")
        return []


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
        db_conn_and_lock = libinspector_state.db_conn_and_lock
        if db_conn_and_lock is not None:
            conn, rw_lock = db_conn_and_lock
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
    hostname = resolve_hostname(ip_addr)
    return hostname


def resolve_hostname(ip_addr: str) -> str:
    try:
        # socket.gethostbyaddr returns a tuple: (hostname, alias list, ipaddr list)
        hostname, _, _ = socket.gethostbyaddr(ip_addr)
        return hostname
    except socket.herror:
        # This is specifically for "Host not found"
        return ""
    except Exception:
        # Using logger.exception to capture the traceback automatically
        logging.exception(f"Unexpected error resolving hostname for {ip_addr}")
        return ""


# """
# Fetches the product name of a device using its MAC address.
# updates the cache periodically, like 5 mins
# Args:
#     mac_address (str): The MAC address of the device.
# Returns:
#     str: The product name of the device or 'Unknown Device' if not found.
# """

# TODO: Ask libinspector team if they have plans to store the product names in the server
# Note: Currently hard coded
# TODO: Add 
@ttl_cache(maxsize=8192, ttl=300)
def get_product_name_by_mac(mac_address: str) -> str:
    device_custom_name = common.get_device_custom_name(mac_address)
    if device_custom_name.startswith('Unknown Device'):
        return 'unknown'
    _,  model_name = find_best_match(device_custom_name)
    return model_name if model_name else 'unknown'

    """with model.db:
        # Query the database for the device with the specified MAC address
        device = model.Device.select(model.Device.product_name).where(
            model.Device.mac_addr == mac_address
        ).first()

        # Return the product name if the device exists, otherwise return a default value
        return device.product_name if device and device.product_name else 'Unknown Device'"""
    

@ttl_cache(maxsize=128)
def protocol_transform(test_protocols: list) -> str:
    # for i in range(len(test_protocols)):
    if 'TCP' in test_protocols:
        result = 'TCP'
    elif 'MQTT' in test_protocols:
        result = 'TCP'
    elif 'UDP' in test_protocols:
        result = 'UDP'
    elif 'TLS' in test_protocols:
        result = 'TCP'
    else:
        result = str(test_protocols)
    if ';' in result:
        tmp = result.split(';')
        result = ' & '.join(tmp)
    return result


# transform multiple hosts to single host
@ttl_cache(maxsize=128)
def host_transform(test_hosts: str) -> str:
    # process host
    if test_hosts is None:
        return 'non'

    if test_hosts!= '':
        try:
            tmp = test_hosts.split(';')
        except Exception:
            return 'non'
        test_hosts= tmp[0]
    else:
        return 'non'

    test_hosts = test_hosts.lower()   
    test_hosts = test_hosts.replace('?','')
    return test_hosts
