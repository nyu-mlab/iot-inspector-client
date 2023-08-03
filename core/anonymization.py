import functools
import hashlib
import core.config as config
import uuid
import threading



_get_user_id_lock = threading.Lock()



@functools.lru_cache(maxsize=1024)
def get_device_id(mac_addr: str) -> str:
    """
    Returns an anonymized MAC address.

    """
    mac_addr = mac_addr.replace(':', '').lower()
    return get_hash(mac_addr)



def get_hash(input_str: str) -> str:
    """
    Returns a HMAC of the input string with user_id, using SHA-256, and
    return the first 16 bytes.

    """
    user_id = get_user_id()
    input_str = input_str + user_id

    return hashlib.sha256(input_str.encode('utf-8')).hexdigest()[:16]



@functools.lru_cache(maxsize=1)
def get_user_id() -> str:
    """
    Returns the randomly generated user ID at installation time.

    """
    with _get_user_id_lock:
        try:
            return config.get('user_id')
        except KeyError:
            user_id = uuid.uuid4().hex
            config.set('user_id', user_id)
            return user_id