# -*- coding: utf-8 -*-

import re


def as_seconds(secs):
    """
    Return a duration string as seconds
    """
    if isinstance(secs, (int, float,)):
        return int(secs)

    # exact seconds
    m = re.match(r'^\d+$', secs)
    if m:
        return int(secs)

    # minutes
    m = re.match(r'^(\d+)m(?!on)(in)?', secs, re.I)
    if m:
        return int(int(m.group(1)) * 60)

    # hours
    m = re.match(r'^(\d+)h', secs, re.I)
    if m:
        return int(m.group(1)) * 3600

    # days
    m = re.match(r'^(\d+)d', secs, re.I)
    if m:
        return int(m.group(1)) * 86400

    # weeks
    m = re.match(r'^(\d+)w', secs, re.I)
    if m:
        return int(m.group(1)) * 86400 * 7

    # months
    m = re.match(r'^(\d+)mon', secs, re.I)
    if m:
        return int(int(m.group(1)) * 86400 * 365 / 12)

    # years
    m = re.match(r'^(\d+)y', secs, re.I)
    if m:
        return int(m.group(1)) * 86400 * 365

    raise ValueError(secs)
