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


# Returns a list of all mac_address values from the devices table.

@ttl_cache(ttl=30)
def get_mac_address_list() -> list:
    """
    Returns a list of all mac_address values from the devices table.
    Assumes the table 'devices' exists and conn is a valid DB connection.
    """
    try:
        conn, rw_lock = libinspector_state.db_conn_and_lock
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
def get_product_name_by_mac(mac_address):
    if mac_address == '20:fe:00:d0:c2:9b':
        return 'amazon-plug'
    if mac_address == 'b0:f7:c4:6f:30:7f':
        return 'echoshow5'
    if mac_address == '0c:dc:91:8f:55:4d':
        return 'echoshow5'
    if mac_address == '192.166.1.?':
        return 'ring-camera' 
    if mac_address == 'a8:6e:84:ed:84:bd':
        return 'tplink-bulb'
    if mac_address == '192.166.1.?':
        return 'yi-camera'
    if mac_address == '192.166.1.?':
        return 'ring-camera'
    if mac_address == '192.166.1.?':
        return 'wyze-cam'
    if mac_address == 'e0:9d:13:31:2c:6a':
        return 'samsung-tv'
    
    return 'unknown'

    """with model.db:
        # Query the database for the device with the specified MAC address
        device = model.Device.select(model.Device.product_name).where(
            model.Device.mac_addr == mac_address
        ).first()

        # Return the product name if the device exists, otherwise return a default value
        return device.product_name if device and device.product_name else 'Unknown Device'"""
    

@ttl_cache(maxsize=128)
def protocol_transform(test_protocols):
    # for i in range(len(test_protocols)):
    if 'TCP' in test_protocols:
        test_protocols = 'TCP'
    elif 'MQTT' in test_protocols:
        test_protocols = 'TCP'
    elif 'UDP' in test_protocols:
        test_protocols = 'UDP'
    elif 'TLS' in test_protocols:
        test_protocols = 'TCP'
    if ';' in test_protocols:
        tmp = test_protocols.split(';')
        test_protocols = ' & '.join(tmp)
    return test_protocols


# transform multiple hosts to single host
@ttl_cache(maxsize=128)
def host_transform(test_hosts):
    # process host
    if test_hosts == None:
        return 'non'

    if test_hosts!= '':
        try:
            tmp = test_hosts.split(';')
        except:
            return 'non'
        test_hosts= tmp[0]
    else:
        return 'non'

    test_hosts = test_hosts.lower()   
    test_hosts = test_hosts.replace('?','')   

    return test_hosts
