Running flow
----------------
packet_processor.py -> burst_processor.py -> feature_generation.py -> feature_standardization.py

packet_processor: 
gets raw packets from libinspector.core via page_manager
preprocess raw packets: removes arp/dns/ssdp packets, duplicate packets

bust_processor: 
gets tcp/udp packets from packet processor 
transfer packets to burst according to the window size 

feature_generation:
gets burst from bust_processor
creates features from burst 

