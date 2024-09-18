"""
An in-memory cache that expires keys after a given time.

# Example usage
cache = KeyValueCache()
cache.set('key1', 'value1')
cache.set('key2', 'value2')

print(cache.get('key1'))  # Output: value1
print(cache.get('key2'))  # Output: value2

time.sleep(5)

print(cache.get('key1'))  # Output: None (expired)
print(cache.get('key2'))  # Output: None (expired)

"""
import threading
import time


class KeyValueCache:

    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()

    def set(self, key, value, expiration=5):
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expiration_time': time.time() + expiration
            }

    def get(self, key):
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if item['expiration_time'] > time.time():
                    return item['value']
                else:
                    del self._cache[key]
        return None

