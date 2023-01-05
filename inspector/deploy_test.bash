#!/bin/bash

# Exit when any command fails
set -e

# Compile the driver

rm -rf dist/

# Below for testing only
# pyinstaller --onedir --nowindow --add-data="network_traffic.schema.sql:." --add-data="configs.schema.sql:." generate_mock_data.py

# Below for deployment
pyinstaller \
    --onedir \
    --nowindow \
    --name="Inspector" \
    --add-data="network_traffic.schema.sql:." \
    --add-data="configs.schema.sql:." \
    --add-data="maxmind-country.mmdb:." \
    --add-data="oui.txt:." \
    --add-data="icon.png:." \
    --add-data="../env/lib/python3.9/site-packages/netdisco:./netdisco" \
    --add-data="../env/lib/python3.9/site-packages/dns:./dns" \
    start.py

# Compress the AppleScript app

rm -f /tmp/inspector_test.app.zip
zip /tmp/inspector_test.app.zip -r inspector_test.app/

# Compress driver

cd dist/Inspector
zip /tmp/driver.zip -r *
cd -

# Upload all necessary files

rsync -azv --progress inspector_test.bash /tmp/driver.zip /tmp/inspector_test.app.zip mlab:/var/www/html/tmp-share/inspector-test/
