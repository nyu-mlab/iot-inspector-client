"""
API that integrates the front end with the core Inpsector functionalities.

"""

import utils
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, StreamingResponse
from typing import List
import uvicorn
import settings
from models import *
import io



# Configure FastAPI doc interface
class DocTags:
    GLOBAL_STATE = 'Global State'
    DEVICE_MANAGEMENT = 'Device Management'
    DEVICE_STATS = 'Device Statistics'
    MISC = 'Miscellaneous'


tags_metadata = [
    {
        'name': DocTags.GLOBAL_STATE,
        'description': 'Controls the state of Inspector'
    },
    {
        'name': DocTags.DEVICE_MANAGEMENT,
        'description': 'Lists and manages devices'
    },   
    {
        'name': DocTags.DEVICE_STATS,
        'description': 'Statistics of device network activities'
    },   
    {
        'name': DocTags.MISC,
        'description': 'Miscellaneous functions'
    }
]

# Initialize API server
app = FastAPI(
    title='Inspector Local API',
    description='API for web UI to interact with the core Inspector components',
    version=settings.VERSION,
    openapi_tags=tags_metadata
)
app.mount(
    '/dashboard', 
    StaticFiles(directory=os.path.join(
        utils.get_current_file_dir(), '..', 'ui', 'default')
    ), 
    name="static_files"
)


@app.get('/get_global_config', tags=[DocTags.GLOBAL_STATE], response_model=GlobalConfig)
def get_global_config() -> GlobalConfig:
    """
    Returns the global configuration, which includes the following fields:

    - **has_consent**: Whether the user has provided consent to use Inspector.
    
    - **contribute_data**: Whether the user agrees to contribute data to
      research.
    
    - **auto_inspect_new_devices**: Whether Inspector automatically inspects new
      devices.
    
    - **is_inspecting**: Whether Inspector is currently inspecting or trying to
      inspect any devices. If this is set to true, then Inspector will inspect
      all devices that are marked for inspection. If this is set to false, then
      all devices that are marked for inspection will not be inspected.

    """
    return GlobalConfig()


@app.get('/get_custom_option/{option_key}', tags=[DocTags.GLOBAL_STATE], response_model=dict)
def get_custom_option(option_key: str) -> dict:
    """
    Returns the value for the given `option_key` in the form of `{option_key:
    option_value}`. If `option_key` has not been set yet, returns an empty
    dictionary `{}`.

    This method is for the UI to recall/retrieve some custom state (set using
    `set_custom_option`) that is not defined in this API.

    For example, the UI may want to show the welcome screen only once. To
    remember whether the user has seen the screen, the UI could call
    (hypothetically) `/get_custom_option/user_has_seen_welcome_screen`. If this
    is the first time the user has seen the welcome screen, then this call will
    return `{}`. In this case, Inspector can show the welcome screen and call
    `/get_custom_option/user_has_seen_welcome_screen/true`. The next time the
    user opens Inspector, we check
    ``/get_custom_option/user_has_seen_welcome_screen` and it will return
    `{"user_has_seen_welcome_screen": "true"}` -- in which case we don't show
    the welcome screen again.
    
    """
    return {}


@app.get('/set_custom_option/{option_key}/{option_value}', tags=[DocTags.GLOBAL_STATE])
def set_custom_option(option_key: str, option_value: str):
    """
    Sets the value for the given `option_key`.

    This method is for the UI to remember some custom state that is not defined
    in this API, so that the UI could recall/retrieve it later using the
    `get_custom_option` method.
    
    """
    return 



@app.get('/set_global_config', tags=[DocTags.GLOBAL_STATE])
def set_global_config(config: GlobalConfig):
    """
    Sets the global configuration

    """
    return


@app.get('/exit', tags=[DocTags.GLOBAL_STATE])
def exit():
    """
    Terminates Inspector.

    """
    return    


@app.get('/get_device_list', tags=[DocTags.DEVICE_MANAGEMENT], response_model=List[DeviceState])
def get_device_list() -> List[DeviceState]:
    """
    Returns a list of devices and their state attributes, including:

    - **device_id**: unique identifier of the device
    - **is_inspected**: whether Inspector is currently inspecting the device's
      activities
    - **is_blocked**: whether Inspector should block the device while Inspector is
      running.
    - **user_device_name**: user-specified name of the device; it should include
      the vendor's name
    - **auto_device_name**: automatically inferred name of the device
    - **ip_addr**: local IP address of the device
    - **mac_addr**: MAC address of the device
    - **tag_list**: a list of strings for tagging the device (as set by the user)

    This list constantly gets updated as Inspector discovers more devices. The
    UI should call this method as often as possible (e.g., around once per
    second), but not too frequently as it would incurr unnecessary disk IO. 

    """
    return []


@app.get('/set_device_state/{device_id}', tags=[DocTags.DEVICE_MANAGEMENT], response_model=DeviceState)
def set_device_state(device_id: str, device_state: DeviceState) -> DeviceState:
    """
    Sets the device state for device with `device_id`.
    Returns the complete `DeviceState` of the device.

    You don't have to specify every attribute in the DeviceState. 
    Just specify the attribute you'd like to set, 
    except the following attributes (which Inspector sets automatically and are thus read-only):
    - device_id
    - auto_device_name
    - ip_addr
    - mac_addr

    If you set the above read-only attributes, Inspector will simply ignore your requests.    

    For example, if you just want to start inspecting a device with `device_id`
    123, you can use the following curl command:

    ```
    curl -X 'GET' \\
    'http://127.0.0.1:53721/set_device_state/123' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "device_id": "123",
    "is_inspected": true
    }'
    ```

    As another example, if you want to add a tag to the same device, you need to
    first obtain the list of existing tags by calling `/get_device_list`. Let's
    say the existing tags are `['TagA', 'TagB']`. To add a new tag `TagC`, you call:

    ```
    curl -X 'GET' \\
    'http://127.0.0.1:53721/set_device_state/123' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "device_id": "123",
    "tag_list": ["TagA", "TagB", "TagC"]
    }'
    ```

    """
    return device_state


@app.get('/block', tags=[DocTags.DEVICE_MANAGEMENT])
def download_all_data():
    """
    Downloads a JSON file of all device data.
    
    """
    return StreamingResponse(io.StringIO('Test Data'))



@app.get('/download_all_data', tags=[DocTags.DEVICE_MANAGEMENT])
def download_all_data():
    """
    Downloads a JSON file of all device data.
    
    """
    return StreamingResponse(io.StringIO('Test Data'))


@app.get('/delete_all_research_data', tags=[DocTags.DEVICE_MANAGEMENT])
def delete_all_research_data():
    """
    Deletes all data that that user has contributed to research.
    
    """
    return 


@app.get('/get_device_network_activities/{device_id}', tags=[DocTags.DEVICE_STATS], response_model=List[DeviceNetworkActivity])
def get_device_network_activities(device_id, activity_filter: DeviceNetworkActivityFilter) -> List[DeviceNetworkActivity]:
    """
    Returns a list of `DeviceNetworkActivity` of a device, given its
    `device_id`, based on filters set in `DeviceNetworkActivityFilter`.

    If Inspector did not capture any network activities for the device, or if
    there are no activities after we applied the filter, then this method
    returns an empty list.

    Parameters for `DeviceNetworkActivityFilter`:
    
    - **start_ts**: starting time (in unix timestamp) for the activities
      (inclusive). If this is 0, then this method returns all activities up to
      and including `end_ts`.
    
    - **end_ts**: end time (in unix timestamp) for the activities (inclusive).
      If this is 0, then this method returns all activities starting from
      `start_ts` to the latest. If both `start_ts` and `end_ts` are set to 0,
      then this method returns all activities for the device.
    
    - **granularity**: time (in seconds) for roughly how often this method
      reports the activities. Let's say a device sends X bytes in the first 0.3
      seconds, Y bytes in the next 0.7 seconds, followed by Z bytes in the next
      second. If `granularity` is set to 1, then this method will report that
      the device sends (X+Y) bytes at time = 0 sec, Z bytes at time = 1 sec, and
      0 bytes at time = 2 sec. If `granularity` is set to 2, then this method
      will report that the device sends (X+Y+Z) bytes at time = 0 sec, and 0
      bytes at time = 2 sec.

    Once the filter is set, this method returns a list of
    `DeviceNetworkActivity`, which includes the following fields:

    - **device_id**: The device of interest.

    - **counterparty_device_id**: The device of interest is talking to which other
      device -- which we call the counterparty. This field shows the `device_id`
      of the counterparty. The `counterparty_device_id` must refer to another device on
      the local network.

    - **counterparty_is_local**: Whether the device of interest is talking to
      another local host (as opposed to the Internet).

    - **min_unix_ts** and **max_unix_ts**: The statistics henceforth are for
      activities between the `min_unix_ts` and `max_unix_ts` times (both unix
      timestamps). The difference between these two timestamps are *roughly*
      equal to `granularity`.

    - **protocol**: Could be `tcp`, `udp`, or `others`.

    - **device_ip**, **device_mac**, **counterparty_ip**, **counterparty_mac**:
      IP and MAC addresses of the current device of interest and the
      counterparty.

    - **device_port** and **counterparty_port**: Which ports are used in this
      communication between the device of interest and the counterparty.

    - **counterparty_hostname**: Hostname (based on DNS or SNI) of the
      counterparty if the counterparty is a remote host.

    - **counterparty_human_label**: A human-readable label for
      `counterparty_hostname`. For example, if `counterparty_hostname` is
      `*.doubleclick.net`, then the corresponding
      `counterparty_human_label` could be (for example) "Google
      Advertising Services".

    - **counterparty_country**: Two-letter country code for where the
      counterparty might be located -- if the counterparty is a remote host.

    - **counterparty_is_ad_tracking**: Whether the counterparty is an
      advertising and tracking service, given that `counterparty_is_local` is
      False.

    - **inbound_byte_count** and **outbound_byte_count**: How many bytes are
      coming into the device of interest, and how many bytes are going out.

    - **activity_human_label**: What the device is really doing in a way that is
      human readable. 

    
    """
    return []


@app.get('/get_device_counterparties/{device_id}/{timeframe}', tags=[DocTags.DEVICE_STATS], response_model=List[Device_CounterpartyStats])
def get_device_counterparties(device_id, timeframe) -> List[Device_CounterpartyStats]:
    """
    Returns a list of counterparties and their statistics seen on the device
    with `device_id`, given `timeframe` (see docs for
    `get_overall_device_stats`). 

    Most of the attributes for `Device_CounterpartyStats` can be found in previous
    docs, except for:

    - **uses_weak_encryption** and **uses_no_encryption**: Whether the communication between `device_id` and this counterparty uses weak encryption and no encryption respectively.

    - **inbound_byte_count** and **outbound_byte_count**: How many bytes are coming into this device (i.e., inbound/download) and going out of this device (i.e., outbound/upload). All inbound/outbound references are with respect to devices (not counterparties).

    - **last_updated_ts**: Unix timestamp for when the above statistics were updated in the database.

    """
    return []


@app.get('/get_overall_device_stats/{device_id}/{timeframe}', tags=[DocTags.DEVICE_STATS], response_model=OverallDeviceStats)
def get_overall_device_stats(device_id, timeframe) -> OverallDeviceStats:
    """
    Returns the overall statistics given a device with `device_id` within the
    past `timeframe` seconds.

    For example, if you want to show statistics in the past 24 hours, set
    `timeframe` to be (24 * 3600) = 86400 seconds. If you want to show
    statistics for the entire history, set `timeframe` to 0.

    The returned device statistics include the following fields:

    - **min_ts** and **max_ts**: The minimum and maximum unix timestamps for the
      device activities.

    - **active_seconds**: Inspector has captured the activities of this device
      for how many seconds. Note that `active_seconds` is always less than or
      equal to `max_ts` - `min_ts`.

    - **total_inbound_byte_count** and **total_outbound_byte_count**. How many
      bytes are received (inbound) and sent (outbound) in total.

    - **weak_encryption_inbound_byte_count** and
      **weak_encryption_outbound_byte_count**. How many bytes are received
      (inbound) and sent (outbound) in total over an weak encrypted channel
      (i.e., encrypted with insecure cipher, or outdated encryption).

    - **no_encryption_inbound_byte_count** and
      **no_encryption_outbound_byte_count**. How many bytes are received
      (inbound) and sent (outbound) in total over an unencrypted channel.

    - **ad_tracking_inbound_byte_count** and
      **ad_tracking_outbound_byte_count**. How many bytes are received (inbound)
      and sent (outbound) in total from/to advertising and tracking services.

    - **inbound_byte_count_dict** and **outbound_byte_count_dict**. How many
      bytes are received (inbound) and sent (outbound) to different
      counterparties. Here, the dictionary's keys are the counterparties'
      hostnames, and the values are the byte counts. To show user-friendly names
      of the counterparty hostnames (i.e., `counterparty_human_label`), you can
      either call `get_all_counterparties` (fast, as it gives you all the
      counterparties at one go) or `get_counterparty_human_label` (slow, as
      you'd have to query the counterparties one by one).

    - **counterparty_country_list** and **counterparty_ad_tracking_list**: For
      the counterparties, list their countries and names of ad/tracking
      companies (if any).
    
    """
    return OverallDeviceStats()


@app.get('/get_all_counterparties/{timeframe}', tags=[DocTags.DEVICE_STATS], response_model=List[CounterpartyStats])
def get_all_counterparties(timeframe) -> List[CounterpartyStats]:
    """
    Returns a list of counterparties and their statistics seen across all the
    devices, given `timeframe` (see docs for `get_overall_device_stats`). 

    Most of the attributes for `CounterpartyStats` can be found in previous
    docs, except for:

    - **data_out_flow_dict**: A dict that captures how many bytes of traffic
      each inspected device has sent to the current counterparty. Here, each key
      is a `device_id`, and the coresponding value is the number of bytes sent
      (i.e., outbound) from the device to the current counterparty. You can use
      the keys of this dictionary to list all devices that sent data to a given
      counterparty.

    - **weak_encryption_device_list** and **no_encryption_device_list**: A list
      of `device_id`s such that each device communicated with the current
      counterparty using weak encryption and no encryption respectively.
    
    """
    return []


@app.get('/get_counterparty_human_label/{counterparty_hostname}', tags=[DocTags.DEVICE_STATS], response_model=str)
def get_counterparty_human_label(counterparty_hostname) -> str:
    """
    Given `counterparty_hostname`, returns the human readable label.

    For example, if `counterparty_hostname` is `*.doubleclick.net, then this
    call returns 'Google Advertising Service'.
    
    """
    return ''


@app.get('/get_overall_bandwidth_consumption', tags=[DocTags.DEVICE_STATS], response_model=BandwidthConsumption)
def get_overall_bandwidth_consumption() -> BandwidthConsumption:
    """
    Returns the overall bandwidth consumption in both inbound (download) and
    outbound (upload) directions.
    
    """
    return BandwidthConsumption()


@app.get('/', tags=[DocTags.MISC])
def root_page():
    """Returns the homepage."""
    return RedirectResponse('/dashboard/html/index.html')


def start_local_api_server():
    return uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=settings.LOCAL_API_WEBSERVER_PORT, 
        workers=1
    )


if __name__ == '__main__':
    start_local_api_server()
