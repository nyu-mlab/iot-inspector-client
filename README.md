# Smart Home Inspector

This branch is for the development of the new Inspector -- a collaboration
between NYU, Consumer Reports, and Ocopop.


## For Alpha Testers

Currently, you can test Inspector only on macOS. We've tested it on macOS Monterey (M1 and Intel) and Ventura (M1).

See the download link:

https://github.com/nyu-mlab/iot-inspector-client/releases/tag/v2.0.0-alpha

If you're curious how this binary works, download the zip file, unzip it, and open the binary in macOS Script Editor. You'll see that the binary is just a fancy wrapper around the installation script (`inspector_test.bash`). Danny pushes updates using the `deploy_test.bash` script. Check out these scripts in the `cr-dev` branch!


## For Developers

### Run the Python Driver

(The code does NOT work on Linux or Windows yet.)

On macOS, do the following to set up the environment and test Inspector.

Make sure you have Python 3. Do the following from the command line:

```
git clone https://github.com/nyu-mlab/iot-inspector-client.git
cd iot-inspector-client
git checkout cr-dev
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
sudo mkdir /Applications/inspector
sudo python inspector/start.py
```

(If you're on Ubuntu 20, you might encounter an error where `Python.h` is not found. In this case, before doing `pip install -r requirements.txt`, you need to run `sudo apt-get install python3-dev`.)




Issues? Questions? Please create an Issue.


### Run the UI Server

Make sure that you're still on the `cr-dev` branch. Return to the `iot-inspector-client` directory.

```
cd ui/default
yes | yarn install:all
yes | yarn client:build
yes | yarn prisma:generate
sudo yarn dev
```





## Documentation

### System Design

![inspector-system-design](https://user-images.githubusercontent.com/1479070/170374526-d2fa9156-c386-41bb-94ea-17ea5bbfe595.png)

[Source File of Diagram](https://drive.google.com/file/d/1NPmysXA42BwZnroqAikgl_3HbTHSimJH/view)




