import pytest
import json
import time
from tests.api.utils.api_client import ApiClient
from tests.api.utils.auth_helper import AuthenticationHelper

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
def check_health(api_client):
    """
    Runs before any tests to verify API health.
    Stops test session if healthcheck fails.
    """
    for _ in range(3):
        response = api_client.get("/ping")
        if response.status_code == 201:
            print(f"\nHealthcheck passed: {response.status_code}")
            return
        time.sleep(2)
    pytest.fail("API healthcheck failed after 3 retries!")


@pytest.fixture(scope="session")
def create_test_booking(api_client):
    payload = {
        "firstname": "Test",
        "lastname": "User",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-09-10",
            "checkout": "2025-09-11"
        },
        "additionalneeds": "Breakfast"
    }
    response = api_client.post("/booking", data=payload)
    assert response.status_code == 200, f"Booking creation failed: {response.text}"
    
    booking_data = response.json()
    # booking_id = booking_data["bookingid"]
    print(f"\nBooking created successfully: {json.dumps(booking_data, indent=2)}")
    return booking_data
    