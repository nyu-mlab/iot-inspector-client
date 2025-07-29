Running flow
----------------
plan: event-detection models will run locally
packet_processor.py -> burst_processor.py -> feature_generation.py -> feature_standardization.py -> periodic_filter.py

packet_processor: 
gets raw packets from libinspector.core via page_manager
preprocess raw packets: removes arp/dns/ssdp packets, duplicate packets

bust_processor: 
gets tcp/udp packets from packet processor 
transfer packets to burst according to the window size 

feature_generation:
gets burst from bust_processor
creates features from burst 

feature_standardization:
standerdiuze feature 

## Plan: Local LLM Agent

### Install Dependentcy
`sudo uv pip install mac-vendor-lookup`



## Step-by-Step Plan: Lightweight LLM Agent

### 🧱 Step 1: Install Dependencies

`pip install transformers datasets accelerate peft trl bitsandbytes`

✅ bitsandbytes enables quantized models (4-bit, 8-bit) to save memory.