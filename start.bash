#!/bin/bash

source env/bin/activate

cd frontend

sudo -E env PATH=$PATH streamlit run dashboard.py --server.port 33761 --browser.gatherUsageStats false --server.headless true --server.baseUrlPath "inspector_dashboard"