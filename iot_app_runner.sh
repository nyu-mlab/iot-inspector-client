#!/usr/bin/env bash

dir=~/iot_inspector
branch=cr-dev

run_mac(){
    
    ## free up occupied ports
    lsof -i:3000 -t | xargs kill -9
    lsof -i:4000 -t | xargs kill -9

    if test ! $(which brew); then 
        echo "Installing homebrew..." 
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)" 
        echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
        echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.bashrc
        echo 'export PATH="/opt/homebrew/sbin:$PATH"' >> ~/.bashrc
    fi

    if test ! $(which python3); then
        echo "Installing python3..."
        ruby -e "$(brew install python3)"
    fi

    if test ! $(which node); then
        echo "Installing nodejs..."
        ruby -e "$(brew install node)"
    fi

    if test ! $(which yarn); then
        echo "Intalling yarn..."
        npm install --global yarn
    fi

    if test ! $(which git); then
        echo "Installing git..."
        ruby -e "$(brew install git)"
    fi

    if [ ! -d "$dir" ]; then
        echo "$dir does not exist."
        git clone https://github.com/nyu-mlab/iot-inspector-client.git $dir
        cd $dir
        git checkout $branch

        python3 -m venv ~/iot_inspector_env
        source ~/iot_inspector_env/bin/activate
        
        cd $dir
        pip3 install -r requirements.txt
        
        cd $dir/ui/default
        yarn install:all
        yarn clean:db
        yarn prisma:generate
    fi

    ## run python driver
    
    trap terminate SIGINT
    terminate(){
        echo "Terminating app"
       
        deactivate
        pkill -SIGINT -P $$
        # kill $(pgrep -f 'python3 start.py')
        
    } 

    source ~/iot_inspector_env/bin/activate
    cd $dir/ui/default && yarn dev &
    sleep 5

    echo "app running on http://localhost:4000"
    open http://localhost:4000

    sleep 2
    clear;
    osascript -e 'do shell script "cd ~/iot_inspector/inspector && sudo python3 start.py" with administrator privileges'
    # cd ~/iot_inspector/inspector && sudo python3 start.py  
}

run_linux(){
 # free port 3000 & 4000
    lsof -i:3000 -t | xargs kill -9
    lsof -i:4000 -t | xargs kill -9

    if test ! $(which python3); then
        sudo apt-get update
        echo "Installing python3..."
        ruby -e "$(sudo apt-get install python3.9)"
    fi

    if test ! $(which node); then
        echo "Installing nodejs..."
        ruby -e "$(sudo apt-get install nodejs)"
    fi

    if test ! $(which yarn); then
        echo "Intalling yarn..."
        npm install --global yarn
    fi

    if test ! $(which git); then
        echo "Installing git..."
        ruby -e "$(sudo apt-get install git)"
    fi

    if [ ! -d "$dir" ]; then
        echo "$dir does not exist."
        git clone https://github.com/nyu-mlab/iot-inspector-client.git $dir
        cd $dir
        git checkout $branch

        python3 -m venv ~/iot_inspector_env
        source ~/iot_inspector_env/bin/activate

        cd $dir/inspector
        pip3 install -r requirements.txt

        cd $dir/ui/default
        yarn install:all
        yarn clean:db
        yarn prisma:generate
    fi

    ## run python driver
    
    trap terminate SIGINT
    terminate(){
        echo "Terminating app"
        deactivate
        pkill -SIGINT -P $$
        # kill $(pgrep -f 'python start.py')
    } 
    
    source ~/iot_inspector_env/bin/activate

    cd $dir/ui/default && yarn dev &
    sleep 5

    echo "app running on http://localhost:4000"
    xdg-open http://localhost:4000

    sleep 2
    clear;
    cd $dir/inspector && sudo python3 start.py 
}

if [ "$(uname)" == "Darwin" ]; then
    # Do something under Mac OS X platform    
    run_mac    
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Do something under GNU/Linux platform
    run_linux
fi
