"""
Parses and extracts the company based on the MAC address.

"""
import functools
import core.common as common
import os


# Maps the first 3 (or more) bytes of the MAC address to the company name.
_oui_dict = {}

_oui_length_split_list = []



@functools.lru_cache(maxsize=1)
def parse_wireshark_oui_database():

    _oui_length_splits = set()

    wireshark_oui_db_file_path = os.path.join(common.get_python_code_directory(), 'wireshark_oui_database.txt')

    with open(wireshark_oui_db_file_path, encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue
            (oui, _, company) = line.split('\t')
            oui = oui.split('/', 1)[0].lower().replace(':', '').strip()
            _oui_dict[oui] = company.strip()
            _oui_length_splits.add(len(oui))

    _oui_length_split_list.extend(sorted(_oui_length_splits))



@functools.lru_cache(maxsize=1024)
def get_vendor(mac_addr: str) -> str:
    """Given a MAC address, returns the vendor. Returns '' if unknown. """

    parse_wireshark_oui_database()

    mac_addr = mac_addr.lower().replace(':', '').replace('-', '').replace('.', '')

    # Split the MAC address in different ways and check against the oui_dict
    for split_length in _oui_length_split_list:
        oui = mac_addr[:split_length]
        if oui in _oui_dict:
            return _oui_dict[oui]

    return ''



def test():

    assert get_vendor('74:F8:DB:E0:00:00') == 'Bernard Krone Holding GmbH & Co. KG'
    assert get_vendor('8C:1F:64:00:30:00') == 'Brighten Controls LLP'
    assert get_vendor('8C:1E:80:00:00:00') == 'Cisco Systems, Inc'



if __name__ == '__main__':
    test()
