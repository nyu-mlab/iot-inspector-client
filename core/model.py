import core.common as common
from peewee import *
import os
import json
import uuid
import threading


# Should be held whenever writing to the database.
write_lock = threading.Lock()


# Create the project directory if it doesn't exist yet
project_directory = common.get_project_directory()
if not os.path.exists(project_directory):
    os.makedirs(project_directory)


# Create the database
db_path = os.path.join(common.get_project_directory(), 'data.sqlite3')
db = SqliteDatabase(
    db_path,
    pragmas={'journal_mode': 'wal'}
)


class BaseModel(Model):
    class Meta:
        database = db


class Device(BaseModel):

    # Auto populated by Inspector
    mac_addr = TextField(index=True)
    ip_addr = TextField(index=True)

    # Data collected about this device by Inspector; if type list, must be JSON friendly
    dhcp_hostname = TextField(default="")
    user_agent = TextField(default="")
    upnp = TextField(default="")
    mdns = TextField(default="")

    # User-labeled data
    vendor = TextField(default="")
    product_name = TextField(default="")
    icon_id = IntegerField(null=True)
    image_base64 = TextField(default="")
    tag_list = TextField(default="[]")

    # Friendly info inferred from NYU cloud
    friendly_vendor = TextField(default="")
    friendly_product = TextField(default="")

    # Device state
    is_inspected = IntegerField(default=1)
    donates_data = IntegerField(default=0)
    is_blocked = IntegerField(default=0)
    favorite_time = FloatField(default=0)

    # TCP scan results
    open_tcp_ports = TextField(default="[]")

    # Banner grab results
    port_banners = TextField(default="{}") # {port1:[banner1.1, banner1.2, banner1.3], port2:[banner2.1, banner2.2., banner2.3]} 


class Flow(BaseModel):

    start_ts = FloatField(index=True)
    end_ts = FloatField()
    src_device_mac_addr = TextField(index=True)
    dst_device_mac_addr = TextField(index=True)
    src_port = IntegerField(null=True)
    dst_port = IntegerField(null=True)
    src_ip_addr = TextField(index=True)
    dst_ip_addr = TextField(index=True)
    src_country = TextField(default="")
    dst_country = TextField(default="")
    src_hostname = TextField(default="", index=True)
    dst_hostname = TextField(default="", index=True)
    src_reg_domain = TextField(default="")
    dst_reg_domain = TextField(default="")
    src_tracker_company = TextField(default="")
    dst_tracker_company = TextField(default="")
    protocol = TextField(default="")
    byte_count = IntegerField()
    packet_count = IntegerField()


class Hostname(BaseModel):

    device_mac_addr = TextField(index=True)
    hostname = TextField(index=True)

    ip_addr = TextField(default="", index=True)
    reg_domain = TextField(default="")
    is_advertising = IntegerField(default=0)
    data_source = TextField(default="")


class FriendlyIdentity(BaseModel):

    key = TextField(index=True)
    value = TextField()
    type = TextField(index=True)


class Configuration(BaseModel):

    key = TextField(index=True)
    value = TextField()


class AdTracker(BaseModel):

    hostname = TextField(index=True)
    tracker_company = TextField(default='')


class SSDPInfoModel(BaseModel):

    mac = TextField(default="")

    scan_time = FloatField(default=0)
    location = TextField(default="")
    ip = TextField(default="")
    port = TextField(default="")
    outer_file_name = TextField(default="")

    # The response of ssdp:discover request (already decoded by utf-8)
    # list[str]. May have multiply responses but the location is the same
    # Some unstructured information will be included here, such as server infomation and uuid
    original_reply = TextField(default="")

    # For the location given by the first response, we request the file and parse it.
    server_string = TextField(default="")
    device_type = TextField(default="")
    friendly_name = TextField(default="")
    manufacturer = TextField(default="")
    manufacturer_url = TextField(default="")
    model_description = TextField(default="")
    model_name = TextField(default="")
    model_number = TextField(default="")

    # This attribute is list[dict]. We need to use json.loads() and json.dumps()
    services_list = TextField(default="")


class mDNSInfoModel(BaseModel):

    mac = TextField(default="") 

    scan_time = FloatField(default=0)
    ip = TextField(default="")
    status = TextField(default="")
    # This attribute is list[dict{str:str, str:list[dict]……}]
    services = TextField(default="") 


def initialize_tables():
    """Creates the tables if they don't exist yet, and creates initial data."""

    with db:

        # Create tables
        db.drop_tables([Device, Flow, Hostname, FriendlyIdentity, Configuration, AdTracker, SSDPInfoModel, mDNSInfoModel])
        db.create_tables([Device, Flow, Hostname, FriendlyIdentity, Configuration, AdTracker, SSDPInfoModel, mDNSInfoModel])
