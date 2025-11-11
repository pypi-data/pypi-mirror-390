from dataclasses import dataclass
from gtfs_loader import schema
from typing import List

from ..gofs_file import GofsFile
from datetime import datetime, timedelta

FILENAME = 'calendars'

DAYS_OF_WEEK = {
    'monday': 'mon',
    'tuesday': 'tue',
    'wednesday': 'wed',
    'thursday': 'thu',
    'friday': 'fri',
    'saturday': 'sat',
    'sunday': 'sun'
}

@dataclass
class Calendar:
    calendar_id: str
    start_date: str
    end_date: str
    days: List[str]
    excepted_dates: List[str]


def create(gtfs, used_calendar_ids):
    used_calendar_ids_copy = used_calendar_ids.copy() # Make a copy to avoid modifying the original list
    calendars = extract_calendar(gtfs, used_calendar_ids_copy)
    calendars.extend(extract_calendar_dates_only_calendar(gtfs, used_calendar_ids_copy))

    return GofsFile(FILENAME, created=True, data=calendars)

def extract_calendar(gtfs, used_calendar_ids):
    calendars = []
    for calendar in gtfs.calendar.values():
        if calendar.service_id not in used_calendar_ids:
            continue  # Only extract calender that are actually used by on demand services

        days_of_week = extract_service_days_of_week(calendar)
        start_date = repr(calendar.start_date)
        end_date = repr(calendar.end_date)
        if service_id_had_added_calendar_dates(calendar.service_id, gtfs):
            calendar_data = handle_added_service_dates(gtfs, calendar, start_date, end_date, days_of_week)
        else:
            excepted_dates = get_excepted_dates(gtfs, calendar)

            calendar_data = Calendar(calendar.service_id, start_date, end_date, days_of_week, excepted_dates)
        
        used_calendar_ids.remove(calendar.service_id)
        calendars.append(calendar_data)
    return calendars

def handle_added_service_dates(gtfs, calendar, start_date, end_date, days_of_week):
    start_date_dt = datetime.strptime(start_date, '%Y%m%d')
    end_date_dt = datetime.strptime(end_date, '%Y%m%d')

    valid_dates = []
    current_date = start_date_dt
    while current_date <= end_date_dt:
        if current_date.strftime('%a').lower()[:3] in days_of_week:
            valid_dates.append(current_date.strftime('%Y%m%d'))
        current_date += timedelta(days=1)

    added_dates = []
    if calendar.service_id in gtfs.calendar_dates:
        for calendar_date in gtfs.calendar_dates[calendar.service_id]:
            if calendar_date.exception_type is schema.ExceptionType.ADD:
                added_dates.append(repr(calendar_date.date))

    excepted_dates = get_excepted_dates(gtfs, calendar)

    valid_dates = set(valid_dates)
    excepted_dates = set(excepted_dates)
    added_dates = set(added_dates)

    final_dates = (valid_dates - excepted_dates) | added_dates
    final_dates = sorted(list(final_dates))

    calendar_data = create_calendar_with_list_dates(calendar.service_id, final_dates)
    return calendar_data

def get_excepted_dates(gtfs, calendar):
    excepted_dates = []
    if calendar.service_id in gtfs.calendar_dates:
        for calendar_date in gtfs.calendar_dates[calendar.service_id]:
            if calendar_date.exception_type is schema.ExceptionType.REMOVE:
                excepted_dates.append(repr(calendar_date.date))
    return excepted_dates

def service_id_had_added_calendar_dates(service_id, gtfs):
    if service_id not in gtfs.calendar_dates:
        return False

    for calendar_date in gtfs.calendar_dates[service_id]:
        if calendar_date.exception_type is schema.ExceptionType.ADD:
            return True

    return False

def extract_calendar_dates_only_calendar(gtfs, used_calendar_ids):
    calendars = []
    for calendar_id in used_calendar_ids:
        # Remaining calendar ids should be from calendar_dates, otherwise they are just missing
        if calendar_id in gtfs.calendar_dates:
            active_dates_calendar = []
            for calendar_date in gtfs.calendar_dates[calendar_id]:
                if calendar_date.exception_type is schema.ExceptionType.ADD:
                    if repr(calendar_date.date) not in active_dates_calendar:
                        active_dates_calendar.append(repr(calendar_date.date))
                elif calendar_date.exception_type is schema.ExceptionType.REMOVE:
                    if repr(calendar_date.date) in active_dates_calendar:
                        active_dates_calendar.remove(repr(calendar_date.date))

            calendar_data = create_calendar_with_list_dates(calendar_id, active_dates_calendar)
            calendars.append(calendar_data)
    return calendars

def create_calendar_with_list_dates(calendar_id, active_dates_calendar):
    # take a list of dates, and create a calendar with all the dates with a list of exception for all the missing dates
    # workaround for the lack of support for a list of supported dates in GOFS
    active_dates_calendar.sort()
    start_date = active_dates_calendar[0]
    end_date = active_dates_calendar[-1]

    start_date_dt = datetime.strptime(start_date, '%Y%m%d')
    end_date_dt = datetime.strptime(end_date, '%Y%m%d')

    all_dates = set()
    current_date = start_date_dt
    while current_date <= end_date_dt:
        all_dates.add(current_date.strftime('%Y%m%d'))
        current_date += timedelta(days=1)

    active_dates_set = set(active_dates_calendar)
    missing_dates = all_dates - active_dates_set

    excepted_dates = sorted(list(missing_dates))

    days = list(DAYS_OF_WEEK.values())
    calendar_data = Calendar(calendar_id, start_date, end_date, days, excepted_dates)
    return calendar_data

def extract_service_days_of_week(calendar):
    days = []
    for day_attr, day_str in DAYS_OF_WEEK.items():
        if getattr(calendar, day_attr):
            days.append(day_str)
    return days
