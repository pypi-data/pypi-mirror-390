import os
import re

__RED_STRING = '\033[91m{}\033[00m' if os.isatty(0) else '{}'
__GREEN_STRING = '\033[92m{}\033[00m' if os.isatty(0) else '{}'
__YELLOW_STRING = '\033[93m{}\033[00m' if os.isatty(0) else '{}'


def red_text(text):
    return __RED_STRING.format(text)


def green_text(text):
    return __GREEN_STRING.format(text)


def yellow_text(text):
    return __YELLOW_STRING.format(text)


def concat_url(*args):
    url = '/'.join([*args])
    url = re.sub(r'(?<!:)//', r'/', url)
    return url


def get_zones(gtfs):
    zones = dict()
    for zone in gtfs.locations["features"]:
        zones[zone["id"]] = zone
    return zones


def get_locations_group(gtfs):
    location_groups = {}  # groupe_id -> [zone_id...]
    for group_id, group in gtfs.location_groups.items():
        location_groups.setdefault(group_id, [])
        for location in group:
            location_groups[group_id].append(location["location_id"])

    return location_groups