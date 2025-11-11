import time
from pathlib import Path
from copy import copy

from .default_headers import get_default_headers
from .utils import green_text, red_text

from .files import calendars
from .files import fares
from .files import gofs
from .files import gofs_versions
from .files import operation_rules
from .files import service_brands
from .files import system_information
from .files import vehicle_types
from .files import wait_time
from .files import wait_times
from .files import booking_rules
from .files import zones

from .gofs_data import GofsData

GOFS_VERSION = '1.0'


def save_files(files, filepath, ttl, creation_timestamp, split_by_route):
    print(f'split_by_route:{split_by_route}')

    if not split_by_route:
        # Simple case where we just dumb everything as a single GOFS folder
        save_files_single_folder(files, filepath, ttl, creation_timestamp)
        return 

    # At this point, we need to create one GOFS folder per route
    save_files_one_folder_per_route(files, filepath, ttl, creation_timestamp)


def save_files_single_folder(files, filepath, ttl, creation_timestamp):
    for file in files.values():
        file.save(filepath, ttl, GOFS_VERSION, creation_timestamp)


def save_files_one_folder_per_route(files, filepath, ttl, creation_timestamp):
    # Grab unique route id
    routes = set()
    for rule in files['operating_rules'].data:
        routes.add(rule.brand_id)

    # For each route, save a gofs folder
    for route_id in routes:
        route_folder = Path(filepath / route_id)
        route_folder.mkdir(parents=True, exist_ok=True)

        for filename, file in files.items():
            if filename == 'operating_rules':
                # Filter all rule that aren't part of the current route
                file_copy = file.copy_with(data=[operating_rule for operating_rule in file.data if operating_rule.brand_id == route_id])
                file_copy.save(route_folder, ttl, GOFS_VERSION, creation_timestamp)
                continue
            
            file.save(route_folder, ttl, GOFS_VERSION, creation_timestamp)


def register_created_file(files_created, file):
    if not file.created:
        print('Skipped', red_text(file.get_filename_with_ext()))
        return

    print(green_text(file.get_filename_with_ext()), 'successfully created')
    files_created[file.filename] = file


def has_convertable_data(gtfs):
    """Check if a valid locations.geojson file was loaded."""
    return gtfs.locations != {}


def convert_to_gofs(gtfs, gofs_dir, ttl, base_url, split_by_route=False, timestamp=None, itineraries=False):
    if not has_convertable_data(gtfs):
        return GofsData()

    if timestamp is not None:
        creation_timestamp = timestamp
    else:
        creation_timestamp = int(time.time())

    default_headers_template = get_default_headers(
        ttl, GOFS_VERSION, creation_timestamp)

    files_created = {}

    file, gofs_data = operation_rules.create(gtfs, itineraries=itineraries)
    register_created_file(files_created, file)

    file = zones.create(gtfs, gofs_data)
    register_created_file(files_created, file)

    file = system_information.create(gtfs)
    register_created_file(files_created, file)

    file = service_brands.create(gtfs, gofs_data.route_ids)
    register_created_file(files_created, file)

    file = vehicle_types.create(gtfs)
    register_created_file(files_created, file)

    file = calendars.create(gtfs, gofs_data.calendar_ids)
    register_created_file(files_created, file)

    file = fares.create(gtfs)
    register_created_file(files_created, file)

    file = wait_times.create(gtfs, gofs_data.pickup_booking_rule_ids)
    register_created_file(files_created, file)

    file = wait_time.create(gtfs)
    register_created_file(files_created, file)

    file = booking_rules.create(gtfs, gofs_data.pickup_booking_rule_ids)
    register_created_file(files_created, file)

    file = gofs_versions.create(default_headers_template, base_url)
    register_created_file(files_created, file)

    file = gofs.create(gtfs, base_url, files_created)
    register_created_file(files_created, file)

    save_files(files_created, gofs_dir, ttl, creation_timestamp, split_by_route)
