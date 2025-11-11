class GofsData:
    """
    Contain the different ids of data extracted from the GTFS-Flex
    Used to know what to extract in the other files
    """

    def __init__(self):
        self.transfers = set()
        self.route_ids = set()
        self.calendar_ids = set()
        self.pickup_booking_rule_ids = {}
        self.zones_ids = set()

    def register_transfer(self, transfer):
        self.transfers.add(transfer)

    def register_route_id(self, route_id):
        self.route_ids.add(route_id)

    def register_calendar_id(self, used_calendar_id):
        self.calendar_ids.add(used_calendar_id)

    def register_pickup_booking_rule_id(self, pickup_booking_rule_id, transfer):
        if pickup_booking_rule_id == None or pickup_booking_rule_id == '':
            return
    
        self.pickup_booking_rule_ids.setdefault(
            pickup_booking_rule_id, set()).add(transfer)

    def register_zone_id(self, zone_id):
        self.zones_ids.add(zone_id)

    def __repr__(self) -> str:
        return f'transfers: {repr(self.transfers)}\nroute_ids: {repr(self.route_ids)}\ncalendar_ids: {repr(self.calendar_ids)}\npickup_booking_rule_ids: {repr(self.pickup_booking_rule_ids)}'


class GofsTransfer:
    """
    A single zone to zone microtransit-like transfer
    """

    def __init__(self, trip_id, from_stop_id, to_stop_id):
        self.trip_id = trip_id
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id

    def __repr__(self):
        return 'Transfer(from_stop_id: {}, to_stop_id: {}, trip_id:{})'.format(self.from_stop_id, self.to_stop_id, self.trip_id)
