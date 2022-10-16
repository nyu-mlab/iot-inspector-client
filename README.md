# Smart Home Inspector

This branch is for the development of the new Inspector -- a collaboration
between NYU, Consumer Reports, and Ocopop.


## For internal testers

So far, we are still working on an easily deployable version. Until then, all testers would have to use the command line to test-drive the latest Inspector.

The following instructions assume that a tester uses macOS Big Sur and/or above, and that they have a basic understanding of the macOS Terminal.

You can also view a video walkthrough here: https://www.loom.com/share/ffbfff6db53d44bdb495952b58eb757d

### Run the Python driver

1. Run the following in the Terminal:

```
mkdir ~/cr-dev
cd ~/cr-dev
git clone https://github.com/nyu-mlab/iot-inspector-client.git
cd ~/cr-dev/iot-inspector-client
git checkout cr-dev # Switch to the CR branch
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt # Set up dependencies
cd ~/cr-dev/iot-inspector-client/inspector
sudo python start.py # Run the Python driver
```

2. Keep the above running, which automatically captures traffic from ALL devices on the network.


### Setting up the UI

Do the following in a separate terminal window.

1. Install the Homebrew package manager: https://brew.sh/

2. Install Yarn on the terminal:
```
brew install yarn
```

3. Spin up the UI on the terminal:
```
cd ~/cr-dev/iot-inspector-client/ui/default
yarn install:all  # This will install dependencies within server and client
yarn prisma:generate  # This will compile a prisma server for your OS/architecture.
yarn dev # Run the UI
```

4. Open any browser and navigate to http://localhost:4000




## Setting up the development environment

### For all developers

On Linux and macOS, do the following to set up the environment and test Inspector.

Make sure you have Python 3. Do the following from the command line:

```
git clone https://github.com/nyu-mlab/iot-inspector-client.git
cd iot-inspector-client
git checkout cr-dev
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python inspector/start.py
```

If you're on Ubuntu 20, you might encounter an error where `Python.h` is not found. In this case, before doing `pip install -r requirements.txt`, you need to run `sudo apt-get install python3-dev`.

Issues? Questions? Please create an Issue.


### For UI/UX developers:

[This section is subject to change, as the UI/UX developers will be using
nodejs. The Python client and nodejs will communicate over a sqlite database.]

Edit the files within the `ui/default` directory. The HTML for the start page
must be `ui/default/html/index.html`. Feel free to place any other files (e.g.,
images, CSS, and JS) elsewhere in the `ui/default` directory. Make sure to
commit your changes in the `cr-dev` branch.

To test the UI, start Inspector and navigate to http://localhost:53721/, which
automatically redirects to `/dashboard/html/index.html`.



## Documentation

### System Design

![inspector-system-design](https://user-images.githubusercontent.com/1479070/170374526-d2fa9156-c386-41bb-94ea-17ea5bbfe595.png)

[Source File of Diagram](https://drive.google.com/file/d/1NPmysXA42BwZnroqAikgl_3HbTHSimJH/view)




