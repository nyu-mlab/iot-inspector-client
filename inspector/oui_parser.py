oui_dict = {}

with open('oui.txt') as fp:
    for line in fp:
        try:
            (oui, vendor) = line.strip().split(',', 1)
        except Exception:
            continue

        oui_dict[oui] = vendor


def get_vendor(oui):

    try:
        return oui_dict[oui]
    except KeyError:
        return '(Unknown)'