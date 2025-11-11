import pytest
from unittest.mock import Mock
from gtfs_flex_to_gofs.files.operation_rules import get_type_of_trip, TripType


class MockStopTime:
    def __init__(self, start_pickup_drop_off_window=-1, end_pickup_drop_off_window=-1):
        self.start_pickup_drop_off_window = start_pickup_drop_off_window
        self.end_pickup_drop_off_window = end_pickup_drop_off_window


def test_regular_service_classification():
    """Test that trips with only regular stops (no regions) are classified as REGULAR_SERVICE"""
    stop_times = [
        MockStopTime(),  # Regular stop
        MockStopTime(),  # Regular stop
        MockStopTime(),  # Regular stop
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.REGULAR_SERVICE


def test_pure_microtransit_classification():
    """Test that trips with only regions are classified as PURE_MICROTRANSIT"""
    stop_times = [
        MockStopTime(0, 300),    # Region
        MockStopTime(300, 600),  # Region
        MockStopTime(600, 900),  # Region
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.PURE_MICROTRANSIT


def test_deviated_service_classification():
    """Test that trips with stops and regions (alternating pattern) are classified as DEVIATED_SERVICE"""
    stop_times = [
        MockStopTime(),          # Regular stop
        MockStopTime(0, 300),    # Region 
        MockStopTime(),          # Regular stop
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.DEVIATED_SERVICE


def test_deviated_service_with_multiple_stops_and_regions():
    """Test deviated service with multiple stops and regions"""
    stop_times = [
        MockStopTime(),          # Regular stop
        MockStopTime(0, 300),    # Region
        MockStopTime(),          # Regular stop
        MockStopTime(300, 600),  # Region
        MockStopTime(),          # Regular stop
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.DEVIATED_SERVICE


def test_other_classification_consecutive_regions():
    """Test that trips with consecutive regions are classified as OTHER"""
    stop_times = [
        MockStopTime(),          # Regular stop
        MockStopTime(0, 300),    # Region
        MockStopTime(300, 600),  # Region (consecutive with previous)
        MockStopTime(),          # Regular stop
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.OTHER


def test_other_classification_mixed_with_insufficient_stops():
    """Test that trips with mixed stops/regions but only 2 stops are classified as OTHER"""
    # Only 2 stops with mixed types - not pure microtransit, not deviated service
    stop_times = [
        MockStopTime(),          # Regular stop
        MockStopTime(0, 300),    # Region
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.OTHER


def test_region_detection_start_window_only():
    """Test that a stop with only start_pickup_drop_off_window set is considered a region"""
    stop_times = [
        MockStopTime(),              # Regular stop
        MockStopTime(start_pickup_drop_off_window=0),  # Region (only start window set)
        MockStopTime(),              # Regular stop
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.DEVIATED_SERVICE


def test_region_detection_end_window_only():
    """Test that a stop with only end_pickup_drop_off_window set is considered a region"""
    stop_times = [
        MockStopTime(),              # Regular stop  
        MockStopTime(end_pickup_drop_off_window=300),  # Region (only end window set)
        MockStopTime(),              # Regular stop
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.DEVIATED_SERVICE


def test_invalid_single_stop_returns_other():
    """Test that trips with single stop return OTHER"""
    stop_times = [
        MockStopTime(),  # Single stop - invalid
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.OTHER


def test_invalid_empty_stops_returns_other():
    """Test that trips with no stops return OTHER"""
    stop_times = []
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.OTHER


def test_minimum_valid_regular_service():
    """Test minimum valid case - 2 regular stops"""
    stop_times = [
        MockStopTime(),  # Regular stop
        MockStopTime(),  # Regular stop
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.REGULAR_SERVICE


def test_minimum_valid_microtransit():
    """Test minimum valid case - 2 regions"""
    stop_times = [
        MockStopTime(0, 300),    # Region
        MockStopTime(300, 600),  # Region
    ]
    
    result = get_type_of_trip(stop_times)
    assert result == TripType.PURE_MICROTRANSIT
