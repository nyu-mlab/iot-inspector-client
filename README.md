# Smart Home Inspector

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



### For UI/UX developers:

Edit the files within the `ui/default` directory. The HTML for the start page
must be `ui/default/index.html`.

To test the UI, start Inspector and navigate to http://localhost:53721/, which automatically redirects to `/dashboard/html/index.html`.

The UI interacts with the Inspector client via an local API. See the local API
docs by running Inspector above and navigating to http://127.0.0.1:53721/redoc
or http://localhost:53721/docs (depending on your personal preference). 




## Documentation

### Overview





For the design doc, please refer to the wiki.

For the API doc, you can view it here: TBD




