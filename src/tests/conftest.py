import pytest
import json
import time
from tests.api.utils.api_client import ApiClient
from tests.api.utils.auth_helper import AuthenticationHelper
from tests.api.utils.booking_data_builder import BookingDataBuilder


@pytest.fixture(scope="session")
def config():
    """
    Load test configuration (base_url, credentials, etc.) 
    from resources/config/config.json once per test session.
    """
    with open("resources/config/config.json") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def auth_token(config):
    """
    Generate an authentication token for the session 
    using configured username and password.
    """
    return AuthenticationHelper.get_token(
        config["base_url"],
        config["username"],
        config["password"]
    )


@pytest.fixture(scope="session")
def api_client(config, auth_token):
    """
    Provide an API client initialized with base URL and auth token.
    Shared across all tests in the session.
    """
    return ApiClient(base_url=config["base_url"], auth_token=auth_token)


@pytest.fixture(scope="session", autouse=True)
def check_health(config):
    """
    Verify API health once at the start of the test session.
    Runs automatically before the first test.
    Retries up to 3 times with 2s delay before failing the entire run.
    """
    tmp_client = ApiClient(
        base_url=config["base_url"])  # no auth needed for /ping
    for _ in range(3):
        response = tmp_client.get("/ping")
        if response.status_code == 201:
            print(f"\nHealthcheck passed: {response.status_code}")
            return
        time.sleep(2)
    pytest.fail("API healthcheck failed after 3 retries!")


@pytest.fixture(scope="session")
def create_test_booking(booking_registry):
    """
    Creates a single booking dynamically with default BookingDataBuilder values.
    Returns a list with created booking info: booking ID and full payload.
    """

    """Alias to booking_registry for backward compatibility."""
    return booking_registry
    # # Build booking payload using defaults
    # booking_data = BookingDataBuilder().build()

    # # Create booking on server
    # response = api_client.post("/booking", json=booking_data)
    # response.raise_for_status()

    # # Extract booking ID from API response
    # booking_id = response.json()["bookingid"]

    # # Store created booking info (ID + original payload) for test usage
    # created_bookings = [{"bookingid": booking_id, "data": booking_data}]

    # # Log created booking details for debugging / test traceability
    # print(f"\nBooking created: ID={booking_id}, payload={booking_data}")
    
    # # Yield to the test
    # yield created_bookings

    ############################################

    # # Cleanup: delete booking after test
    # delete_response = api_client.delete(
    #     f"/booking/{booking_id}",
    #     headers={"Cookie": f"token={auth_token}"}
    # )
    # if delete_response.status_code == 201:
    #     print(f"Booking {booking_id} deleted successfully after test.")
    # else:
    #     print(f"Failed to delete booking {booking_id}. Status: {delete_response.status_code}, Response: {delete_response.text}")



@pytest.fixture(scope="session")
def booking_registry(api_client, auth_token):
    """
    Creates all valid bookings from filters.json at session start,
    stores them in a registry for test use, and deletes them at session teardown.
    """
    # Load filters.json
    with open("resources/test-data/filters.json") as f:
        filters = json.load(f)

    registry = []

    # Create bookings for valid=true filters
    for entry in filters:
        if entry.get("valid", False):
            params = entry.get("params", {})
            booking_payload = BookingDataBuilder(params).build()

            # POST booking
            response = api_client.post("/booking", json=booking_payload)
            response.raise_for_status()
            booking_id = response.json()["bookingid"]

            registry.append({"bookingid": booking_id, "data": booking_payload})
            print(f"Booking created: ID={booking_id}, params={params}")

    # Yield the registry to tests
    yield registry

    # Teardown: delete all created bookings
    for booking in registry:
        booking_id = booking["bookingid"]
        delete_response = api_client.delete(
            f"/booking/{booking_id}",
            headers={"Cookie": f"token={auth_token}"}
        )
        if delete_response.status_code == 201:
            print(f"Booking {booking_id} deleted successfully.")
        else:
            print(
                f"Failed to delete booking {booking_id}. "
                f"Status: {delete_response.status_code}, Response: {delete_response.text}"
            )