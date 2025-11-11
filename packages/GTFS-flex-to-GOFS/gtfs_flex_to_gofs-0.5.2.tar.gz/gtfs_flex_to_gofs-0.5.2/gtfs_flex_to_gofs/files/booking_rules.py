from dataclasses import dataclass
from gtfs_loader.schema import BookingType, GTFSTime
from typing import List

from ..gofs_file import GofsFile

FILENAME = 'booking_rules'


@dataclass
class BookingRules:
    from_zone_ids: List[str]
    to_zone_ids: List[str]
    booking_type: BookingType
    prior_notice_duration_min: int
    prior_notice_duration_max: int
    prior_notice_last_day: int
    prior_notice_last_time: int
    prior_notice_last_time: int
    prior_notice_start_time: GTFSTime
    prior_notice_calendar_id: int
    message: str
    pickup_message: str
    drop_off_message: str
    phone_number: str
    info_url: str
    booking_url: str


def create(gtfs, pickup_booking_rule_ids):
    booking_rules = []

    for pickup_booking_rule_id, transfers in pickup_booking_rule_ids.items():
        gtfs_booking_rule = gtfs.booking_rules[pickup_booking_rule_id]

        from_ids = set()
        to_ids = set()
        for transfer in transfers:
            from_ids.add(transfer.from_stop_id)
            to_ids.add(transfer.to_stop_id)

        booking_rules.append(BookingRules(
            from_zone_ids=create_sorted_ids_list(from_ids),
            to_zone_ids=create_sorted_ids_list(to_ids),
            booking_type=gtfs_booking_rule.booking_type,
            prior_notice_duration_min=get_value_or_default(gtfs_booking_rule.prior_notice_duration_min, -1),
            prior_notice_duration_max=get_value_or_default(gtfs_booking_rule.prior_notice_duration_max, -1),
            prior_notice_last_day=get_value_or_default(gtfs_booking_rule.prior_notice_last_day, -1),
            prior_notice_last_time=gtfs_booking_rule.prior_notice_last_time,
            prior_notice_start_time=gtfs_booking_rule.prior_notice_start_time,
            prior_notice_calendar_id=gtfs_booking_rule.prior_notice_service_id,
            message=gtfs_booking_rule.message,
            pickup_message=gtfs_booking_rule.pickup_message,
            drop_off_message=gtfs_booking_rule.drop_off_message,
            phone_number=gtfs_booking_rule.phone_number,
            info_url=gtfs_booking_rule.info_url,
            booking_url=gtfs_booking_rule.booking_url,
        ))

    return GofsFile(FILENAME, created=True, data=booking_rules)


def create_sorted_ids_list(ids:set):
    result = list(ids)
    result.sort()
    return result


def get_value_or_default(value, default=None):
    if value is None:
        return default

    return value
