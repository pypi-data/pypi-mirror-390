import pytest

from pathlib import Path
import gtfs_loader
from gtfs_loader import test_support
from gtfs_flex_to_gofs import gofs_converter

import time
time.time = lambda: 0

test_support.init(__file__)


@pytest.mark.parametrize('feed_dir',
                         test_support.find_tests(),
                         ids=lambda test_dir: test_dir.name)
def test_default(feed_dir):
    do_test(feed_dir)


def do_test(feed_dir):
    work_dir = test_support.create_test_data(feed_dir)
    dest_dir = work_dir / "output"
    Path.mkdir(dest_dir)

    gtfs = gtfs_loader.load(work_dir)
    gofs_converter.convert_to_gofs(gtfs, dest_dir, 24 * 60 * 60, '', ("split_by_route" in str(feed_dir)))
    test_support.check_expected_output(feed_dir, dest_dir)

    # Each folder contains both stop_times.txt and itinerary_cells.txt and should produce identical output
    # converting either
    Path.mkdir(dest_dir)
    gtfs = gtfs_loader.load(work_dir, itineraries=True)
    gofs_converter.convert_to_gofs(gtfs, dest_dir, 24 * 60 * 60, '', ("split_by_route" in str(feed_dir)), itineraries=True)
    test_support.check_expected_output(feed_dir, dest_dir)
