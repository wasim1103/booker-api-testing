import pytest
import json
import time
import logging

logger = logging.getLogger(__name__)
from tests.api.utils.booking_helper import find_matching_bookings, validate_booking_by_id, get_bookings

# Load test data's from JSON
with open("resources/test-data/filters.json") as f:
    filter_data = json.load(f)


# -----------------------------
# Retrieve all booking IDs without filters
# -----------------------------
@pytest.mark.parametrize("data", [d for d in filter_data if d["description"] == "No filters"])
def test_Retrieve_all_booking_IDs_without_filters(api_client, create_test_booking, data):
    """Verify retrieving all booking IDs without applying any filters."""

    # Send GET request to /booking endpoint to retrieve all booking IDs
    response = api_client.get("/booking")

    # Verify API responded with HTTP 200 OK
    assert response.status_code == 200

    # Parse JSON response containing all booking IDs
    booking_ids = response.json()

    # Validate response is a non-empty list
    assert isinstance(booking_ids, list), f"Response is not a list"
    assert len(booking_ids) > 0, f"Response is having zero booking"

    # Extract only the booking IDs from the response
    ids = [item["bookingid"] for item in booking_ids]

    # Check that every booking ID is an integer
    assert all(isinstance(bid, int) for bid in ids), f"Not all booking IDs are numbers: {ids}"

    # Print booking IDs for traceability/debugging
    #logger.info(f"Found booking IDs: {ids}")

    # Verify that the dynamically created booking(s) exist in the retrieved IDs
    for booking in create_test_booking:
        booking_id = booking["bookingid"]
        if booking_id in ids:
            logger.info(f"Booking ID {booking_id} found in API response.")
        else:
            logger.error(f"Booking ID {booking_id} NOT found in API response!")
        assert booking_id in ids, f"Booking ID {booking_id} missing from API response {ids}"


# -----------------------------
# Retrieve booking IDs by applying single filters
# -----------------------------
@pytest.mark.parametrize(
    "data",
    [d for d in filter_data if d["description"] == "Individual filter"],
    ids=lambda d: f"{d['description']}-{d['params']}"
)
def test_by_applying_single_filters(api_client, create_test_booking, data):
    """Test Individual filters by applying firstname, lastname, checkin, checkout"""
    booking_to_test = find_matching_bookings(create_test_booking, data["params"])
    booking_id = booking_to_test["bookingid"]

    # Validate that the filtered GET /booking call returns the expected booking ID
    # get_bookings is a helper function that returns a list of IDs matching the filter params
    ids = get_bookings(api_client, data["params"])
    assert booking_id in ids, f"Booking {booking_id} not returned by API filter {data['params']}"

    # Validate that the payload returned by GET /booking/{id} matches the expected booking data
    # Validate_booking_by_id is a helper function that performs field-level validations
    validate_booking_by_id(api_client, booking_to_test, data["params"])


# -----------------------------
# Retrieve booking IDs by applying multiple filters
# -----------------------------
@pytest.mark.parametrize(
    "data",
    [d for d in filter_data if d["description"] == "Multiple filters"],
    ids=lambda d: f"{d['description']}-{d['params']}"
)
def test_by_applying_multiple_filters(api_client, create_test_booking, data):
    """Test Multiple filters by firstname, lastname, checkin, checkout"""
    # Loop through dynamically created bookings for this test session
    booking_to_test = find_matching_bookings(create_test_booking, data["params"])
    booking_id = booking_to_test["bookingid"]

    # Validate that the filtered GET /booking call returns the expected booking ID
    # get_bookings is a helper function that queries the API with multiple filter params
    ids = get_bookings(api_client, data["params"])
    assert booking_id in ids, f"Booking {booking_id} not returned by API filter {data['params']}"

    # Validate that the payload returned by GET /booking/{id} matches the expected booking data
    # validate_booking_by_id checks the field-level data to ensure it matches what was created
    validate_booking_by_id(api_client, booking_to_test, data["params"])


# -----------------------------
# Error handling for invalid filter values
# -----------------------------
@pytest.mark.parametrize(
    "data",
    [d for d in filter_data if d["description"]
     == "Invalid Value Format In filter"],
    ids=lambda d: f"{d['description']}-{d['params']}"
)
def test_Validate_error_handling(api_client, data):
    """Test invalid filters return proper error responses"""
    # Send GET request with invalid filter parameters
    response = api_client.get("/booking", params=data["params"])

    # Log request and response for traceability
    logger.info(f"Request: GET /booking, params={data['params']}")
    logger.info(f"Response status: {response.status_code}")

    # Typical invalid filter requests should fail with a client error
    # (most APIs return 400 Bad Request, but 404/422 are also acceptable depending on backend)
    assert response.status_code in [400, 422],f"Unexpected status code {response.status_code} for params {data['params']}"
    


# -----------------------------
# Basic Performance test for GET /booking endpoint
# -----------------------------
def test_get_booking_performance(api_client):
    """Basic performance validation: Response time < 2 seconds"""

    # Measure start time
    start = time.time()
    response = api_client.get("/booking")

    # Calculate elapsed time for the request
    elapsed = time.time() - start

    # Log status and timing for traceability
    logger.info("Performance test: GET /booking (no filters)")
    logger.info("Response status: %s, Time taken: %.2fs", response.status_code, elapsed)
    
    # Assert API returns 200 OK
    assert response.status_code == 200

    # Assert API responds within acceptable threshold (< 2 seconds)
    assert elapsed < 2
