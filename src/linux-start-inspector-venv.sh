#!/bin/bash

# Let's not hardcode the path.
# cd ~/princeton-iot-inspector/iot-inspector-client/v2-src/

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
	DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
	SOURCE="$(readlink "$SOURCE")"
	[[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

cd $DIR

# Start!
echo "Starting IoT Inspector..."
python3 start_inspector.py

# Update software
#echo "Updating software..."
#git pull

# Install dependencies
#echo "Updating dependencies..."
#./linux-install-dependencies.sh
