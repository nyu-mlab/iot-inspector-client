#!/bin/bash

# Exit when any command fails
set -e

# Compile the driver

rm -rf dist/

pyinstaller --onedir --nowindow --add-data="network_traffic.schema.sql:." --add-data="configs.schema.sql:." generate_mock_data.py

# Compress the AppleScript app

rm -f /tmp/inspector_test.app.zip
zip /tmp/inspector_test.app.zip -r inspector_test.app/

# Compress driver

cd dist/generate_mock_data
zip /tmp/driver.zip -r *
cd -

# Upload all necessary files

rsync -azv --progress inspector_test.bash /tmp/driver.zip /tmp/inspector_test.app.zip mlab:/var/www/html/tmp-share/inspector-test/
