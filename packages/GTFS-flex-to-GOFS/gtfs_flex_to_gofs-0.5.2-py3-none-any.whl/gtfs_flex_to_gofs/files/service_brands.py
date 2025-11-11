from dataclasses import dataclass

from ..gofs_file import GofsFile

FILENAME = 'service_brands'


@dataclass
class ServiceBrand:
    brand_id: str
    brand_name: str
    brand_color: str
    brand_text_color: str


def create(gtfs, route_ids):
    service_brands = []

    for route_id in route_ids:
        route = gtfs.routes[route_id]

        service_brand = ServiceBrand(
            brand_id=route_id,
            brand_name=route.route_short_name if route.route_short_name != '' else route.route_long_name,
            brand_color=route.route_color,
            brand_text_color=route.route_text_color,
        )
        service_brands.append(service_brand)

    service_brands.sort(key=lambda x: x.brand_id)
    return GofsFile(FILENAME, created=True, data=service_brands)
