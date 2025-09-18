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


@pytest.fixture(scope="function")
def create_test_booking(api_client, request):
    """
    Creates a single booking dynamically with default BookingDataBuilder values.
    Returns a list with created booking info: booking ID and full payload.
    """
    # Build booking payload using defaults
    booking_data = BookingDataBuilder().build()

    # Create booking on server
    response = api_client.post("/booking", json=booking_data)
    response.raise_for_status()

    # Extract booking ID from API response
    booking_id = response.json()["bookingid"]

    # Store created booking info (ID + original payload) for test usage
    created_bookings = [{"bookingid": booking_id, "data": booking_data}]

    # Log created booking details for debugging / test traceability
    print(f"\nBooking created: ID={booking_id}, payload={booking_data}")
    return created_bookings
