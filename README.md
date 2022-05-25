# Smart Home Inspector

This branch is for the development of the new Inspector -- a collaboration
between NYU, Consumer Reports, and Ocopop.


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

![inspector-system-design](https://user-images.githubusercontent.com/1479070/170168884-89a12848-fd75-45bd-a05b-a7fbc367bb21.png)





