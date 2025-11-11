import argparse
import gtfs_loader
from pathlib import Path

from .gofs_converter import convert_to_gofs
from .patch_gtfs import patch_gtfs
from .utils import yellow_text

DEFAULT_TTL = 86400


def main(args):
    gtfs = gtfs_loader.load(args.gtfs_dir, itineraries=args.itineraries)
    gofs_dir = Path(args.gofs_dir)

    gofs_dir.mkdir(parents=True, exist_ok=True)

    convert_to_gofs(gtfs, gofs_dir, args.ttl, args.url, args.split_by_route, args.timestamp, itineraries=args.itineraries)

    if args.out_gtfs_dir:
        patch_gtfs(args, gtfs, itineraries=args.itineraries)


def print_args_warnings(args):
    if args.url is None:
        print(yellow_text(
            "[WARNING]"), 'No url given. \'gofs.json\' and \'gofs_versions.json\' will not be created. Consider adding a url with the --url parameter')

    if args.ttl == None:
        print(yellow_text(
            '[WARNING]'), 'No ttl given. Will be using the default value of', DEFAULT_TTL)
        args.ttl = DEFAULT_TTL


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert GTFS-flex on-demand format to GOFS')
    parser.add_argument(
        '--gtfs-dir', help='input gtfs directory', metavar='Dir', required=True)
    parser.add_argument(
        '--gofs-dir', help='output gofs directory', metavar='Dir', required=True)
    parser.add_argument(
        '--out-gtfs-dir', help='output directory of patched gtfs', metavar='Dir', required=False)
    parser.add_argument(
        '--url', help='auto-discovery url. Base URL indicate for where each files will be uploaded (and downloadable)')
    parser.add_argument(
        '--ttl', help='time to live of the generated gofs files in seconds (default: 86400)', type=int, default=None)
    parser.add_argument(
        '--no-warning', help='Silence warnings', action='store_true')
    parser.add_argument(
        '--timestamp', help='timestamp for files creation', type=int, default=None)
    parser.add_argument(
        '--split-by-route', help='Split gofs by route', action='store_true')
    parser.add_argument(
        '--itineraries', help='read from transit\'s itinerary_cells format', action='store_true')


    args = parser.parse_args()

    if not args.no_warning:
        print_args_warnings(args)

    main(args)
