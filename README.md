# IoT Inspector 2

**What is IoT Inspector?** An open-source tool for capturing, analyzing, and visualizing the network activities of your smart home devices. It does not require special hardware or changes to your network. Simply run IoT Inspector and you'll see the results instantly. 

You can use IoT Inspector to 

* learn what companies/countries your IoT devices communicate with
* how much data your devices are sending and receiving
* discover any unknown devices on the network
* maybe more? (Tell us please?)

IoT Inspector is a research project by researchers from New York University. See our [main website](https://inspector.engineering.nyu.edu/) and  [documentation](https://github.com/nyu-mlab/iot-inspector-client/wiki) for more information. Also see [screenshots](https://github.com/nyu-mlab/iot-inspector-client/wiki/Screenshots-(Windows)#running-iot-inspector).

**⬇️ Download**:
* Windows 10 & 11: [Download the installer](https://github.com/nyu-mlab/iot-inspector-client/wiki/Download-&-Install) (64-bit, Intel CPU only)
* macOS and Linux: [Run from source code](https://github.com/nyu-mlab/iot-inspector-client/wiki/Download-&-Install#macos); installer/binary coming soon
* Sign up for [our mailing list](https://forms.gle/yrMXoX64hHtPQyNQ6) to receive updates about upcoming releases and research findings!

![overall device activities](https://github.com/nyu-mlab/iot-inspector-client/assets/1479070/671fdea4-4c8d-405e-84d6-ad1b71f4356e)



**🔥 What's new in Version 2**: We released Version 1 in 2019. Since then, we have had 7K+ users who have donated the network traffic from 65K+ devices. We recently launched Version 2 with the following changes:

* Revamped UI/UX
* Decoupled from cloud: You can run IoT Inspector without donating data to us (e.g., in sensitive enterprise environments)
* Extensibility for developers (more details to come)
* See [this article](https://www.usenix.org/publications/loginonline/three-years-crowdsourcing-smart-home-network-traffic) about our experience maintaining IoT Inspector in the last few years.


**🗞️ Media coverage**: See articles about IoT Inspector in the press (all paywalls removed):

* [New York Times](https://www.nytimes.com/2020/01/07/opinion/location-tracking-privacy.html?unlocked_article_code=bXAKhvWOVzlmXYTvb6YR5pJjOmRJaOeRArCoN_dhSv_6RyOPm7LPp1Zna-bMq9DnBbUkm-1qWXH_L7Nhm1_DlM5PZplmF-6O-igOboXPYqWYAs3MTP-Hc0GsZV-_jQYiDIKzD4fQJbZXXPIdy9v9FhKFDOVUyscGBqOKLwod3cramKE80pqApj6-m6du5TqSrPoIiV0gJrRO9tfNxj6PSWPUkhxY5sLIH34qYixu81JS-9LwMgBTr7brUWzIdJtt0wb4syRJoiYXYkXd4LsM1ThHjLr8bufaQ-b75w-3ZFHANpIEgH4NOkDsB0lQBKV3MO0yatl2-cuEpqh5XL8zoZa6bOU&smid=url-share): Why You Should Take a Close Look at What Tracks You. It might help you manage your privacy.

* [National Public Radio](https://www.sciencefriday.com/segments/smart-tv-roku-spying/): Your Smart TV Is Watching You.

* [Washington Post](http://web.archive.org/web/20200727193548/https://www.washingtonpost.com/technology/2019/09/18/you-watch-tv-your-tv-watches-back/?noredirect=on): You watch TV. Your TV watches back.

* [Gizmodo](https://gizmodo.com/this-simple-tool-will-reveal-the-secret-life-of-your-sm-1832264323): This Simple Tool Will Reveal the Secret Life of Your Smart Home

* [TechCrunch](https://techcrunch.com/2019/04/13/spy-on-your-smart-home-with-this-open-source-research-tool/?guccounter=1&guce_referrer=aHR0cHM6Ly9pbnNwZWN0b3IuZW5naW5lZXJpbmcubnl1LmVkdS8&guce_referrer_sig=AQAAAIsGYIGmOZw6fpW-GF03KI87LGhE7Mgp_F27fm5eWTiLu26rPrXdVj-vq_BWCaAuPgfg2AjGVddurkTvX92tYtF7SeELflgPa_PAQ6vNGpddbxU3VEmk4UCzQjKY7tuOikY1W685d_5O6_u7ifyM9N2keBqKjTobUWUSdGijZ65Y): Spy on your smart home with this open source research tool


## Getting started

### Download and install

See [this page](https://github.com/nyu-mlab/iot-inspector-client/wiki/Download-&-Install) if you want to run our precompiled binaries.


### Running from the source code

You will need Python and Git already set up on your system. You'll also need to be familiar with terminals.

#### Tested on macOS Ventura

Run the following in your terminal:

```
git clone https://github.com/nyu-mlab/iot-inspector-client.git
cd iot-inspector-client
python3 -m venv env
source env/bin/activate
pip install -r requirements-general.txt
```

To run, do the following

```
source env/bin/activate
cd ui
./start.bash
```

#### Tested on Windows 10 & 11 with Python 3.8

Run the following in your terminal:

```
git clone https://github.com/nyu-mlab/iot-inspector-client.git
cd iot-inspector-client
python.exe -m venv env
env/Script/activate.bat
pip install -r requirements.txt
```

If you have a more modern version of Python (say Python 3.11), try replacing the last line above with:

```
pip install -r requirements-general.txt
```

To run, do the following in an terminal with administrator's priviledge:

```
env/Script/activate.bat
cd ui
streamlit.exe run Device_List.py --server.port 33761 --browser.gatherUsageStats false --server.headless true --server.baseUrlPath "inspector_dashboard"
```



## Developing for IoT Inspector

To learn how Inspector scans the network and captures the traffic, look at the `core/start.py` file. The relevant modules include `arp_scanner.py`, `arp_spoofer.py`, and `packet_*.py`.

To learn how Inspector constructs the user interface, follow the `ui/start.bash` command.

For details, see our [documentation](https://github.com/nyu-mlab/iot-inspector-client/wiki).



## Questions?

We are still revising the documentation and fixing bugs for IoT Inspector 2. We'd love to hear from you! Here's [how to contact us](https://github.com/nyu-mlab/iot-inspector-client/wiki/Contact-us). Also, here's [more information](https://github.com/nyu-mlab/iot-inspector-client/wiki/Frequently-Asked-Questions#about-iot-inspector) about the IoT Inspector team.
