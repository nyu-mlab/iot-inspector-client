"""
Maintains the global state in a singleton design pattern.
This is separate from the libinspector global state
"""
import threading
import queue

# Should be held whenever accessing the global state's variables.
global_state_lock = threading.Lock()


# A queue that holds raw packets to be processed; stores raw packets;
# page_manager.py uses this queue to get packets to packet_processor.py
packet_queue = queue.Queue()

# A queue that holds packets to be processed for burst creation; stores raw packets;
# packet_processor.py uses this queue to get packets to burst_processor.py
flow_queue = queue.Queue()

# A queue that holds burst that are pending to be processed; 
# stores (flow_key, pop_time, pop_burst) 
# burst_processor.py uses this queue to get bursts to feature_generation.py
pending_burst_queue = queue.Queue()

# A queue that holds processed bursts for further processing;
# stores burst processed to features;
# feature_generation.py uses this queue to get processed bursts to feature_standardization.py
processed_burst = queue.Queue()


# A queue that holds standardized burst features;
# need to discard periodic burst from all bursts;
ss_burst_queue = queue.Queue()

# A queue that holds standardized burst features that are filtered;
filtered_burst_queue = queue.Queue()

# A queue that holds events that are detected;
filtered_event_queue = queue.Queue()