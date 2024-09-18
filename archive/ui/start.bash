#!/bin/bash

 sudo -E env PATH=$PATH streamlit run Device_List.py --server.port 33761 --browser.gatherUsageStats false --server.headless true --server.baseUrlPath "inspector_dashboard"
