"""
Injects traffic into the network to simulate a real network environment.

"""
import core.global_state
import time
import random
import threading


FAKE_VENDORS = [
    'Amazon LLC', 'Google PTE', 'Microsoft Gates Corporation', 'Tim Cook Apple', 'Philips', 'LG', 'Samsung',
    'Sony', 'Nokia', 'Motorola', 'Cisco', 'Dell', 'HP', 'Lenovo', 'Acer',
    'Asus', 'Toshiba', 'Fujitsu', 'Unknown'
]


FAKE_DOMAIN_NAMES = [
    'google.com', 'facebook.com', 'youtube.com', 'baidu.com', 'wikipedia.org', 'yahoo.com', 'reddit.com',
    'qq.com', 'taobao.com', 'amazon.com', 'twitter.com', 'tmall.com', 'instagram.com', 'vk.com', 'live.com',
    'sohu.com', 'sina.com.cn', 'jd.com', 'weibo.com', '360.cn', 'google.co.in', 'google.co.jp', 'google.co.uk',
]


def start_simulation():

    with core.global_state.global_state_lock:
        device_list = core.global_state.context_dict.setdefault('simulated_device_list', [])
        if device_list:
            return
        generate_devices(device_list)

    simulation_thread = threading.Thread(
        target=simulation_helper_thread)
    simulation_thread.daemon = True
    simulation_thread.start()



def simulation_helper_thread():

    while True:
        simulate_traffic()
        time.sleep(1.5)



def simulate_traffic():

    current_ts = int(time.time())

    with core.global_state.global_state_lock:
        for device_alias in core.global_state.context_dict['simulated_device_list']:
            if random.random() < 0.1:

                # Send traffic at 10% probability
                device_dict = core.global_state.outgoing_byte_counter_dict.setdefault(device_alias, dict())
                device_dict[current_ts] = random.randint(1, 1000000)

                # Contacted some hosts
                hostname_dict = core.global_state.recent_hostnames_dict.setdefault(device_alias, dict())
                hostname = random.choice(FAKE_DOMAIN_NAMES)
                hostname_dict[hostname] = current_ts


def generate_devices(device_list, number_of_devices=30):

    for _ in range(number_of_devices):
        device_mac_addr = '00:00:00:' + ':'.join([f'{random.randint(0, 255):02x}' for _ in range(3)])
        vendor = random.choice(FAKE_VENDORS)
        device_alias = f'{vendor} Device {device_mac_addr[-2:].upper()}'
        device_list.append(device_alias)
        print('New device generated:', device_alias)


if __name__ == '__main__':

    start_simulation()

    time.sleep(30)