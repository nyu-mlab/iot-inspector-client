"""
Extract available ports from a list of well-known ports (available_ports_raw.txt).

"""
import re


PORT_REGEX = re.compile(r'^(\d+)')


PORT_DATA_FILE = 'available_ports_raw.txt'


def get_port_list():

    port_set = set([2121])

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
    