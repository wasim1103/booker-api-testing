import pytest
import json
import time
from tests.api.utils.booking_helper import validate_booking_by_id, get_bookings

# Load test data's from JSON
with open("resources/test-data/filters.json") as f:
    filter_data = json.load(f)


# Parametrize test using filter data where description is "No filters"
# This allows the test to run for all relevant entries from the JSON test data
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
    assert all(isinstance(bid, int)
               for bid in ids), f"Not all booking IDs are numbers: {ids}"

    # Print booking IDs for traceability/debugging
    print(f"Found booking IDs: {ids}")

    # Verify that the dynamically created booking(s) exist in the retrieved IDs
    for booking in create_test_booking:
        assert booking["bookingid"] in ids


# Parametrize test using filter data where description is "Individual filter"
# Each entry represents a single filter scenario, e.g., firstname, lastname, checkin, or checkout
# ids=lambda ... ensures that the test ID in reports shows the filter being applied
@pytest.mark.parametrize(
    "data",
    [d for d in filter_data if d["description"] == "Individual filter"],
    ids=lambda d: f"{d['description']}-{d['params']}"
)
def test_by_applying_single_filters(api_client, create_test_booking, data):
    """Test Individual filters by applying firstname, lastname, checkin, checkout"""
    # Loop through dynamically created bookings for this test session
    for booking in create_test_booking:
        booking_id = booking["bookingid"]

    # Validate that the filtered GET /booking call returns the expected booking ID
    # get_bookings is a helper function that returns a list of IDs matching the filter params
    ids = get_bookings(api_client, data["params"])
    assert booking_id in ids, f"Booking {booking_id} not returned by API filter {data['params']}"

    # Validate that the payload returned by GET /booking/{id} matches the expected booking data
    # Validate_booking_by_id is a helper function that performs field-level validations
    validate_booking_by_id(api_client, booking, data["params"])

# Parametrize test using filter data where description is "Multiple filters"
# Each entry represents a combination of filters applied together, e.g., firstname + lastname
# The ids lambda ensures each test case in reports clearly shows which filter combination is being tested


@pytest.mark.parametrize(
    "data",
    [d for d in filter_data if d["description"] == "Multiple filters"],
    ids=lambda d: f"{d['description']}-{d['params']}"
)
def test_by_applying_multiple_filters(api_client, create_test_booking, data):
    """Test Multiple filters by firstname, lastname, checkin, checkout"""
    # Loop through dynamically created bookings for this test session
    for booking in create_test_booking:
        booking_id = booking["bookingid"]

    # Validate that the filtered GET /booking call returns the expected booking ID
    # get_bookings is a helper function that queries the API with multiple filter params
    ids = get_bookings(api_client, data["params"])
    assert booking_id in ids, f"Booking {booking_id} not returned by API filter {data['params']}"

    # Validate that the payload returned by GET /booking/{id} matches the expected booking data
    # validate_booking_by_id checks the field-level data to ensure it matches what was created
    validate_booking_by_id(api_client, booking, data["params"])


# Parametrize test using filter data where description is "Invalid Value Format In filter"
# This test ensures that the API returns proper error responses when invalid filter values are provided
# The ids lambda provides readable test case identifiers in pytest reports
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

    # Print request and response for traceability
    print(f"\nRequest: GET /booking, params={data['params']}")
    print(f"Response status: {response.status_code}")

    # Assert that the API responds with the expected error status code
    assert response.status_code == data["expected_status"]


# Performance test for GET /booking endpoint
def test_get_booking_performance(api_client):
    """Basic performance validation: Response time < 2 seconds"""

    # Measure start time
    start = time.time()
    response = api_client.get("/booking")

    # Calculate elapsed time for the request
    elapsed = time.time() - start

    # Print status and timing for traceability
    print("\nPerformance test: GET /booking (no filters)")
    print(
        f"Response status: {response.status_code}, Time taken: {elapsed:.2f}s")

    # Assert API returns 200 OK
    assert response.status_code == 200

    # Assert API responds within acceptable threshold (< 2 seconds)
    assert elapsed < 2
