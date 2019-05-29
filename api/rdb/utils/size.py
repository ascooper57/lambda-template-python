# -*- coding: utf-8 -*-

import re


def as_size(size):
    """
    Return a size string as an integer
    """
    if isinstance(size, (int, float,)):
        return int(size)

    # exact size in a string
    m = re.match(r'^\d+$', size)
    if m:
        return int(size)

    # gigabytes
    m = re.match(r'^([\d\.]+)gb?$', size, flags=re.I)
    if m:
        return int(float(m.group(1)) * (1000 ** 3))

    # megabytes
    m = re.match(r'^([\d\.]+)mb?$', size, flags=re.I)
    if m:
        return int(float(m.group(1)) * (1000 ** 2))

    # kilobytes
    m = re.match(r'^([\d\.]+)kb?$', size, flags=re.I)
    if m:
        return int(float(m.group(1)) * (1000 ** 1))

    raise ValueError(size)
