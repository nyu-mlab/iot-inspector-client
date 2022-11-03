# Smart Home Inspector

This branch is for the development of the new Inspector -- a collaboration
between NYU, Consumer Reports, and Ocopop.


## For internal testers
* For macOS and Linux

So far, we are still working on an easily deployable version. Until then, all testers would have to use the command line to test-drive the latest Inspector. The following instructions assume that a tester uses macOS Big Sur and/or above, and that they have a basic understanding of the macOS Terminal.

1. Open your terminal.
2. Copy and paste the following command and hit "Enter".
3. macOS will prompt you to enter a password or scan your fingerprint; just comply, because Inspector needs administrator privilege to run.

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/nyu-mlab/iot-inspector-client/cr-dev/iot_app_runner.sh)" 
```

Known issue: When you're done, you can't kill the processes with Control + C. You'd have to kill by doing `sudo pkill -9 -f yarn` and `sudo pkill -9 -f start.py`.

* For windows 64 bit machines

1. Open your terminal.
2. Copy and paste the following command and hit "Enter"
3. If the system doesn't have pre-installed python3, nodejs and/or git, it will make the installations and the user will be prompted to complete these installations first.

```
curl -fsSL https://raw.githubusercontent.com/nyu-mlab/iot-inspector-client/cr-dev/iot_app_runner.bat && iot_app_runner.bat 
```

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




