from datetime import datetime
import json

def validate_booking_by_id(api_client, booking_data, expected_params):
    """
    Retrieve booking by ID and validate fields against expected parameters.
    Handles checkin (>=) and checkout (<=) comparisons.
    """
    booking_id = booking_data["bookingid"]

    # Retrieve booking via API
    response = api_client.get(f"/booking/{booking_id}")
    assert response.status_code == 200, f"Booking {booking_id} not found"

    booking = response.json()
    print(f"\nBooking retrieved successfully: {json.dumps(booking, indent=2)}")

    # Validate fields
    for key, expected_value in expected_params.items():
        if key in ["checkin", "checkout"]:
            actual_date = datetime.strptime(booking["bookingdates"][key], "%Y-%m-%d").date()
            expected_date = datetime.strptime(expected_value, "%Y-%m-%d").date()
            
            if key == "checkin":
                assert actual_date >= expected_date, f"{key} is earlier than expected"
            else:  
                assert actual_date <= expected_date, f"{key} is later than expected"
        else:
            assert booking[key] == expected_value, f"{key} does not match expected value"

    print(f"\nBooking {booking_id} validated successfully against filter")
    return booking


def get_bookings(api_client, filters=None):
    """
    Retrieve booking IDs with optional filters.
    Example filters: {"firstname": "Test", "lastname": "User"}
    """
    params = filters or {}
    response = api_client.get("/booking", params=params)
    assert response.status_code == 200, f"Failed to retrieve bookings: {response.text}"

    booking_ids = [item["bookingid"] for item in response.json()]
    print(f"\nRetrieved {len(booking_ids)} booking(s) with filters {params}: {booking_ids}")
    return booking_ids    


def validate_updated_fields(updated: dict, payload: dict):
    """Ensure payload fields are correctly updated in booking."""
    for key, value in payload.items():
        if key == "bookingdates":
            assert isinstance(updated["bookingdates"], dict), "'bookingdates' should be an object"
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