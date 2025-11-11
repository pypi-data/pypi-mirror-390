from dataclasses import dataclass

from ..gofs_file import GofsFile

FILENAME = 'system_information'


@dataclass
class SystemInformation:
    language: str
    timezone: str
    name: str
    url: str
    subscribe_url: str
    phone_number: str
    short_name: str = ''
    operator: str = ''
    start_date: str = ''
    email: str = ''
    feed_contact_email: str = ''


def create(gtfs):

    info_url = ''
    booking_url = ''
    phone_number = ''

    booking_rules = list(gtfs.booking_rules.values())
    if len(booking_rules) > 0:
        booking_rule = booking_rules[0]
        info_url = booking_rule.info_url
        booking_url = booking_rule.booking_url
        phone_number = booking_rule.phone_number

    agency = list(gtfs.agency.values())[0]

    system_information = SystemInformation(
        language=agency.agency_lang,
        timezone=agency.agency_timezone,
        name=agency.agency_name,
        url=info_url,
        subscribe_url=booking_url,
        phone_number=phone_number,
        # Fields not available in GTFS-Flex
        short_name='',
        operator='',
        start_date='',
        email='',
        feed_contact_email=''
    )

    return GofsFile(FILENAME, created=True, data=system_information)
