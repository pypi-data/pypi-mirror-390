import gtfs_loader
from .files import operation_rules


def patch_gtfs(args, gtfs, itineraries=False):
    clean_up_gtfs(gtfs, itineraries)

    is_empty = len(gtfs.trips) == 0

    if not is_empty:
        gtfs_loader.patch(gtfs, args.gtfs_dir, args.out_gtfs_dir)
    else:
        # we have no data, nothing to export
        print("No data to export, not exporting GTFS")


def clean_up_gtfs(gtfs, itineraries=False):
    trip_ids_to_remove = []
    for trip in gtfs.trips.values():
        stop_times = gtfs.itinerary_cells[trip.itinerary_index] if itineraries else gtfs.stop_times[trip.trip_id]
        if itineraries:
            for i, st in enumerate(stop_times):
                st.start_pickup_drop_off_window = trip.start_pickup_drop_off_windows[i]
                st.end_pickup_drop_off_window = trip.end_pickup_drop_off_windows[i]
        
        type_of_trip = operation_rules.get_type_of_trip(stop_times)
        if type_of_trip == operation_rules.TripType.OTHER:
                print(f"WARNING : Trip {trip.trip_id} is not a normal gtfs trip, not microtransit and not deviated service only. We are not supproting this yet, it will be removed from the GTFS and not shown anywhere")
            
        if type_of_trip == operation_rules.TripType.OTHER or type_of_trip == operation_rules.TripType.PURE_MICROTRANSIT:
            trip_ids_to_remove.append(trip.trip_id)
            if not itineraries:
                del gtfs.stop_times[trip.trip_id]

    for trip_id in trip_ids_to_remove:
        del gtfs.trips[trip_id]
