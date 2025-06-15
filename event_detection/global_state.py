"""
Maintains the global state in a singleton design pattern.
This is separte from the libinspector global state
"""
import threading
import queue

# Should be held whenever accessing the global state's variables.
global_state_lock = threading.Lock()


# A queue that holds packets to be processed
packet_queue = queue.Queue()

