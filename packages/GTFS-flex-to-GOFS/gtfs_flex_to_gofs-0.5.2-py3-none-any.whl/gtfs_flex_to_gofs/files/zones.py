from dataclasses import dataclass
from typing import Any, List

from gtfs_flex_to_gofs.gofs_data import GofsData

from ..gofs_file import GofsFile
from gtfs_flex_to_gofs.utils import get_locations_group, get_zones
import math
import shapely.ops
import json

FILENAME = "zones"
RADIUS_AROUND_STOP_IN_METERS = 1000

@dataclass
class Properties:
    name: str


@dataclass
class Feature:
    zone_id: str
    properties: Properties
    geometry: Any
    type: str = "Feature"


@dataclass
class Zones:
    features: List[Feature]
    type: str = "FeatureCollection"


def create(gtfs, gofs_data: GofsData):
    zones = create_zones_from_geojson(gtfs, gofs_data)
    on_demand_stop_zones = PolygonCreator(
        gtfs, gofs_data, radius=RADIUS_AROUND_STOP_IN_METERS, num_vertices=16
    ).create_zones_from_on_demand_stops()

    result_features = zones + on_demand_stop_zones
    result_features.sort(key=lambda x: x.zone_id)
    return GofsFile(FILENAME, created=True, data=Zones(result_features))


def create_zone(new_zone_id, new_zone_name, new_zone_geometry):
    return Feature(
        zone_id=new_zone_id,
        properties=Properties(
            name=new_zone_name
            # Unused GTFS-flex field
            # zone['properties'].get('stop_desc', '')
            # zone['properties'].get('zone_id', '')
            # zone['properties'].get('stop_url', '')
        ),
        geometry=new_zone_geometry,
    )


def create_zones_from_geojson(gtfs, gofs_data: GofsData):
    zones = []
    for zone in gtfs.locations["features"]:

        if zone["id"] not in gofs_data.zones_ids:
            continue

        new_zone = create_zone(
            new_zone_id=zone["id"],
            new_zone_name=zone["properties"].get("stop_name", ""),
            new_zone_geometry=zone["geometry"],
        )
        zones.append(new_zone)

    return zones


class PolygonCreator:

    def __init__(self, gtfs, gofs_data: GofsData, radius: float, num_vertices: int):
        self.created_zones = []
        self.handled_ids = set()

        self.gtfs = gtfs
        self.gofs_data: GofsData = gofs_data
        self.radius = radius
        self.num_vertices = num_vertices

        self.all_zones = get_zones(gtfs)
        self.all_location_groups = get_locations_group(gtfs)

    def create_zones_from_on_demand_stops(self):
        for transfer in self.gofs_data.transfers:
            self._handle_stop_id(transfer.from_stop_id)
            self.handled_ids.add(transfer.from_stop_id)

            self._handle_stop_id(transfer.to_stop_id)
            self.handled_ids.add(transfer.to_stop_id)

        return self.created_zones

    def _handle_stop_id(self, stop_id):
        if stop_id in self.handled_ids or stop_id in self.all_zones:
            return  # A polygon already exists

        if stop_id in self.all_location_groups:
            self._handle_location_group(stop_id)
        else:
            self._handle_stop(stop_id)

    def _handle_stop(self, stop_id):
        polygon_object = self._create_polygon_from_point_stop(stop_id)
        if polygon_object is None:
            return 
        
        self.created_zones.append(
            create_zone(
            stop_id,
            self.gtfs.stops[stop_id].stop_name,
            json.loads(shapely.to_geojson(polygon_object)),
            )
        )

        self.handled_ids.add(stop_id)

    def _handle_location_group(self, location_group_id):
        feature_list = self._create_feature_list_from_location_group(
            location_group_id
        )

        union_multipolygon = shapely.ops.unary_union(
            feature_list
        )
        geojson_data = json.loads(shapely.to_geojson(union_multipolygon))

        self.created_zones.append(
            create_zone(
                new_zone_id=location_group_id,
                new_zone_name="",
                new_zone_geometry=geojson_data,
            )
        )
        self.handled_ids.add(location_group_id)

    def _create_feature_list_from_location_group(self, location_group_id):
        feature_list = []
        for stop_id in self.all_location_groups[location_group_id]:
            feature_list.append(
                self._create_polygon_from_point_stop(stop_id)
            )

        return feature_list

    def _create_polygon_from_point_stop(self, stop_id):
        if stop_id in self.all_zones:
            polygon_object = shapely.from_geojson(geojson_from_feature_gtfs_object(self.all_zones[stop_id]))
            if not polygon_object.is_valid:
                # Intersecting polygon are not valid, fixing them by adding a buffer of 0. 
                polygon_object = polygon_object.buffer(0)
                if not polygon_object.is_valid: # couln't fix it
                    raise ValueError(f"Invalid polygon for stop_id {stop_id}. Geojson data: {shapely.to_geojson(polygon_object)}")
                else:
                    print(f"Fixed intersecting invalid polygon for location group {stop_id} by buffering it")
            
            return polygon_object

        if stop_id not in self.gtfs.stops:
            print(f"[GTFS-Flex-To-GOFS] - Missing {stop_id} from stops.txt")
            return None
        
        stop = self.gtfs.stops[stop_id]
        if stop.location_type == '101':
            # Location type 101 is a polygon stop, which was already handled
            return None

        new_geometry = self._convert_point_to_circle(
            float(stop.raw_stop_lat), float(stop.raw_stop_lon)
        )

        return shapely.geometry.Polygon(new_geometry)

    def _convert_point_to_circle(self, lat, lng):
        return get_circle_polygon(lat, lng, self.radius, self.num_vertices)

def geojson_from_feature_gtfs_object(feature_object):
    return json.dumps({
        "type": "Feature",
        "properties": {
            "stop_desc": feature_object.properties.stop_desc,
            "stop_name": feature_object.properties.stop_name,
            "stop_url": feature_object.properties.stop_url,
            "zone_id": feature_object.properties.zone_id,
        },
        "geometry": {
            "type": feature_object.geometry.type,
            "coordinates": feature_object.geometry.coordinates,
        }
    })

def get_circle_polygon(lat: float, lng: float, radius: float, numVertices: int):
    coordinates = []

    for idx in range(numVertices):
        circle_frac = -idx / numVertices
        bearing = circle_frac * 2.0 * math.pi
        coordinates.append(offset_circle_vertex(lat, lng, radius, bearing))

    coordinates.append(coordinates[0])  # Close the ring, as per geojson spec
    return coordinates


def offset_circle_vertex(lat: float, lng: float, distance: float, bearing: float):
    EARTH_RADIUS = 6371009.0
    rad_lat_center = (lat * math.pi) / 180.0
    rad_lng_center = (lng * math.pi) / 180.0
    dist_factor = distance / EARTH_RADIUS

    rad_lat = math.asin(
        math.sin(rad_lat_center) * math.cos(dist_factor)
        + math.cos(rad_lat_center) * math.sin(dist_factor) * math.cos(bearing)
    )

    rad_lng = rad_lng_center + math.atan2(
        math.sin(bearing) * math.sin(dist_factor) * math.cos(rad_lat_center),
        math.cos(dist_factor) - math.sin(rad_lat_center) * math.sin(rad_lat),
    )

    # The test framework needs the expected folder to exactly match the generated one
    # and, this algorithm produce slightly different results on different platform on the last 2 digits of a floating number. 
    # Hence, we round them. Anyway, so much precision is useless : https://xkcd.com/2170/
    return (
        round(((rad_lng * 180.0) / math.pi), 10),
        round(((rad_lat * 180.0) / math.pi), 10),
    )
