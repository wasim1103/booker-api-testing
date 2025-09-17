import pytest
import json
import time
import requests
from tests.api.utils.api_client import ApiClient
from tests.api.utils.auth_helper import AuthenticationHelper
from tests.api.utils.booking_data_builder import BookingDataBuilder


@pytest.fixture(scope="session")
def config():
    with open("resources/config/config.json") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def auth_token(config):
    return AuthenticationHelper.get_token(
        config["base_url"],
        config["username"],
        config["password"]
    )


@pytest.fixture(scope="session")
def api_client(config, auth_token):
    return ApiClient(base_url=config["base_url"], auth_token=auth_token)


@pytest.fixture(scope="session", autouse=True)
def check_health(config):
    """Runs before any tests to verify API health."""
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
    booking_id = response.json()["bookingid"]

    created_bookings = [{"bookingid": booking_id, "data": booking_data}]
    print(f"\nBooking created: ID={booking_id}, payload={booking_data}")
    return created_bookings
