"""
Extract available ports from a list of well-known ports (available_ports_raw.txt).

"""
import re


PORT_REGEX = re.compile(r'^(\d+)')


PORT_DATA_FILE = 'available_ports_raw.txt'


def get_port_list():
    port_set = set([2121,
		    11111,
		    1137,
		    123,
		    137,
		    139,
		    1443,
		    1698,
		    1743,
		    18181,
		    1843,
		    1923,
		    19531,
		    22,
		    25454,
		    2869,
		    32768,
		    32769,
		    35518,
		    35682,
		    36866,
		    3689,
		    37199,
		    38576,
		    41432,
		    42758,
		    443,
		    445,
		    45363,
		    4548,
		    46355,
		    46995,
		    47391,
		    48569,
		    49152,
		    49153,
		    49154,
		    49451,
		    53,
		    5353,
		    548,
		    554,
		    56167,
		    56278,
		    56789,
		    56928,
		    59815,
		    6466,
		    6467,
		    655,
		    7676,
		    7678,
		    7681,
		    7685,
		    7777,
		    81,
		    8181,
		    8187,
		    8222,
		    8443,
		    88,
		    8842,
		    8883,
		    8886,
		    8888,
		    8889,
		    911,
		    9119,
		    9197,
		    9295,
		    9999,
		    443,
		    80,
		    993,
		    5228,
		    4070,
		    5223,
		    9543])

    with open(PORT_DATA_FILE) as fp:
        for line in fp:
            port_match = PORT_REGEX.search(line)
            if port_match:
                port = int(port_match.group(1))
                port_set.add(port)

    return sorted(port_set)

def test():

    port_list = get_port_list()

    print('Length:', len(port_list))
    print(port_list)


if __name__ == '__main__':
    test()
    
