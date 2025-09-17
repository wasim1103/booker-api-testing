from datetime import datetime
import json
import time


def validate_booking_by_id(api_client, booking_data, expected_filters):
    """
    Retrieve booking by ID and validate fields against expected filters.
    Handles checkin (>=) and checkout (<=) comparisons.
    """
    booking_id = booking_data["bookingid"]
    response = api_client.get(f"/booking/{booking_id}")
    assert response.status_code == 200, f"Booking {booking_id} not found"
    booking = response.json()
    print(f"\nBooking retrieved successfully: {json.dumps(booking, indent=2)}")

    for key, expected_value in expected_filters.items():
        if key in ["checkin", "checkout"]:
            actual_date = datetime.strptime(
                booking["bookingdates"][key], "%Y-%m-%d").date()
            expected_date = datetime.strptime(
                expected_value, "%Y-%m-%d").date()
            if key == "checkin":
                assert actual_date >= expected_date, f"{key} is earlier than expected"
            else:
                assert actual_date <= expected_date, f"{key} is later than expected"
        elif key in ["firstname", "lastname"]:
            assert booking[key] == expected_value, f"{key} does not match expected value"

    print(f"\nBooking {booking_id} validated successfully against filters")
    return booking


def get_bookings(api_client, filters=None, retries=3, wait=2):
    """
    Retrieve booking IDs from /booking endpoint using filter parameters.
    Retries a few times if no bookings found (handles eventual consistency).
    """
    params = {}
    if filters:
        # Only include allowed query params
        for key in ["firstname", "lastname", "checkin", "checkout"]:
            if key in filters:
                params[key] = filters[key]

    for attempt in range(1, retries + 1):
        response = api_client.get("/booking", params=params)
        assert response.status_code == 200, f"Failed to get bookings: {response.text}"

        booking_list = response.json()
        booking_ids = [b["bookingid"] for b in booking_list]

        if booking_ids:
            print(f"\nRetrieved {len(booking_ids)} booking(s) with filters {params}: {booking_ids}")
            return booking_ids

        print(f"No bookings found for filters {params}. Retry {attempt}/{retries} after {wait}s...")
        time.sleep(wait)

    # Return whatever is retrieved after retries (could be empty)
    print(f"\nAfter {retries} retries, bookings found: {booking_ids}")
    return booking_ids


def validate_updated_fields(updated: dict, payload: dict):
    """Ensure payload fields are correctly updated in booking."""
    for key, value in payload.items():
        if key == "bookingdates":
            assert isinstance(updated["bookingdates"],
                              dict), "'bookingdates' should be an object"
            assert updated["bookingdates"]["checkin"] == value["checkin"]
            assert updated["bookingdates"]["checkout"] == value["checkout"]
        else:
            assert updated[key] == value, f"Field {key} not updated correctly"


def validate_unchanged_fields(original: dict, updated: dict, exclude: list):
    """Ensure all fields except 'exclude' remain unchanged."""
    for key, value in original.items():
        if key in exclude:
            continue
        assert updated[key] == value, f"Field {key} unexpectedly changed"


def wait_for_booking(api_client, booking_id, timeout=10, interval=0.5):
    """
    Polls the server until the booking exists or timeout is reached.
    :param api_client: your ApiClient instance
    :param booking_id: booking ID to check
    :param timeout: maximum time to wait (seconds)
    :param interval: poll interval (seconds)
    :return: True if booking exists, else False
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        response = api_client.get(f"/booking/{booking_id}")
        if response.status_code == 200:
            return True
        time.sleep(interval)
    return False
