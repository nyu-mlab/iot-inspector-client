from pydantic import BaseModel
from typing import List, Dict


class GlobalConfig(BaseModel):
    has_consent: bool = False
    contribute_data: bool = True
    auto_inspect_new_devices: bool = True
    is_inspecting: bool = False


class DeviceState(BaseModel):
    device_id: str = ''
    is_inspected: bool = False
    is_blocked: bool = False
    user_device_name: str = ''
    auto_device_name: str = ''
    ip_addr: str = ''
    mac_addr: str = ''
    tag_list: List[str] = []


class DeviceNetworkActivity(BaseModel):
    device_id: str = ''
    min_unix_ts: int = 0
    max_unix_ts: int = 0
    protocol: str = ''
    device_ip: str = ''
    device_mac: str = ''
    device_port: int = 0
    counterparty_device_id: str = ''
    counterparty_is_local: bool = False
    counterparty_ip: str = ''
    counterparty_mac: str = ''
    counterparty_port: int = 0
    counterparty_hostname: str = ''
    counterparty_hostname_human_label: str = ''
    counterparty_is_ad_tracking: bool = False
    counterparty_country: str = ''
    inbound_byte_count: int = 0
    outbound_byte_count: int = 0
    activity_human_label: str = ''


class DeviceNetworkActivityFilter(BaseModel):
    start_ts: int = 0
    end_ts: int = 0
    granularity: int = 1


class OverallDeviceStats(BaseModel):
    device_id: str = ''
    min_ts: int = 0
    max_ts: int = 0
    active_seconds: int = 0
    inbound_byte_count: int = 0
    outbound_byte_count: int = 0
    inbound_byte_count_dict: Dict[str, int] = {}
    outbound_byte_count_dict: Dict[str, int] = {}
    counterparty_country_list: List[str] = []
    counterparty_ad_tracking_list: List[str] = []    


class CounterpartyStats(BaseModel):
    counterparty_hostname: str = ''
    counterparty_human_label: str = ''
    counterparty_is_ad_tracking: bool = False
    counterparty_country: str = ''
    data_out_flow_dict: Dict[str, int] = {}


class BandwidthConsumption(BaseModel):
    inbound_kbps: int = 0
    outbound_kbps: int = 0