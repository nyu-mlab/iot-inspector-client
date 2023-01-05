# Usage from within AppleScript: bash -l inspector_test.bash [function_name]

BASE_DIR="/Applications/inspector"

COMMIT_ID="5a312fae91a3794bcfc712b1f3c4d83086464d42"

UI_DIR="$BASE_DIR/ui/iot-inspector-client-$COMMIT_ID/ui/default"


# Result to print back to stdout; used for communication with AppleScript
stdout_result="0"


# initialize_directory_structure
mkdir -p $BASE_DIR/ui
mkdir -p $BASE_DIR/driver
mkdir -p $BASE_DIR/tmp


DRIVER_NAME="Inspector"


install_npm() {

    echo "Checking npm version"
    npm --version

    # Install npm if not
    if [ $? -ne 0 ];
    then
        cd $BASE_DIR/tmp/
        echo "Downloading NodeJS"
        curl 'https://nodejs.org/dist/v18.12.1/node-v18.12.1.pkg' >node.pkg
        echo "Installing NodeJS"
        installer -pkg node.pkg -target /
    fi

    # Check if npm is successfully installed
    npm --version
    stdout_result=$?

}


install_yarn() {

    echo "Checking yarn version"
    yarn --version

    # Install yarn if not
    if [ $? -ne 0 ];
    then
        echo "Installing yarn"
        npm install --global yarn
    fi

    # Check if npm is successfully installed
    yarn --version
    stdout_result=$?

}


download_ui_files() {

    cd $BASE_DIR/ui

    if [ ! -f $UI_DIR/package.json ]; then
        echo "Downloading UI files"
        curl https://codeload.github.com/nyu-mlab/iot-inspector-client/zip/$COMMIT_ID 1>source.zip 2>>../tmp/init.log
        echo "Extracting UI files"
        unzip source.zip
    fi

    # Check if the UI files are on disk
    test -f $UI_DIR/package.json
    stdout_result=$?

}


yarn_install_all () {

    if [ ! -f $UI_DIR/yarn_ready ]; then
        echo "Running yarn install:all"
        cd $UI_DIR
        yes | yarn install:all
        stdout_result=$?
    fi

}


yarn_prisma_generate () {

    if [ ! -f $UI_DIR/yarn_ready ]; then
        echo "Running yarn prisma:generate"
        cd $UI_DIR
        yes | yarn prisma:generate
        stdout_result=$?
    fi

}


yarn_client_build () {

    if [ ! -f $UI_DIR/yarn_ready ]; then
        echo "Running yarn client:build"
        cd $UI_DIR
        yes | yarn client:build
        stdout_result=$?
        touch $UI_DIR/yarn_ready
    fi

}


start_ui_server () {

    # Kill any existing servers
    pid_file=$BASE_DIR/yarn_dev.pid
    if [ -f $pid_file ]; then
        kill -9 $(cat $pid_file)
    fi

    # Run the server in the background
    if [ -f $UI_DIR/yarn_ready ]; then
        echo "Running yarn dev"
        cd $UI_DIR
        yarn dev &
        echo $! > $pid_file
    fi

    # Wait at most ten seconds for the server to be up and running.
    for i in {1..10}
    do
        sleep 1
        echo "Checking if the UI server is ready"
        curl http://localhost:3000 >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            break
        fi
    done

    curl http://localhost:3000 >/dev/null 2>&1
    stdout_result=$?

}


download_inspector() {

    if [ ! -f $BASE_DIR/driver/$DRIVER_NAME ]; then
        echo "Downloading the Python driver binary"
        cd $BASE_DIR/driver
        if [[ $(uname -p) == 'arm' ]]; then
            echo "mac M1 chip"
            curl https://mlab.hdanny.org/tmp-share/inspector-test/driver.zip > driver.zip
            unzip driver.zip
        else
            echo "mac Intel chip"
            curl https://mlab.hdanny.org/tmp-share/inspector-test/driver-intel.zip > driver-intel.zip
            unzip driver-intel.zip
        fi

    fi

    test -f $BASE_DIR/driver/$DRIVER_NAME
    stdout_result=$?

}


run_inspector() {

    # Kill any existing driver
    pid_file=$BASE_DIR/driver.pid
    if [ -f $pid_file ]; then
        kill -9 $(cat $pid_file)
    fi

    if [ -f $BASE_DIR/driver/$DRIVER_NAME ]; then
        echo "Running the Python driver binary"
        cd $BASE_DIR/driver
        ./$DRIVER_NAME &
        echo $! > $pid_file
    fi

    # block at most 15 seconds until the database is ready
    for i in {1..15}
    do
        sleep 1
        echo "Checking if the database file is ready"
        if [ -f $BASE_DIR/network_traffic.db ]; then
            break
        fi
    done

    test -f $BASE_DIR/network_traffic.db
    stdout_result=$?

}





# Check if the function exists (bash specific)
# https://stackoverflow.com/questions/8818119/how-can-i-run-a-function-from-a-script-in-command-line
if declare -f "$1" > /dev/null
then
    # call arguments verbatim, logging all outputs
    date >> $BASE_DIR/tmp/init.log
    "$@" >> $BASE_DIR/tmp/init.log 2>&1
    # print result to stdout
    echo "$stdout_result"
else
  # Show a helpful error
  echo "'$1' is not a known function name" >&2
  exit 1
fi