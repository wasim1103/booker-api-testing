import pytest
import json
import time
import logging

import matplotlib.pyplot as plt
import base64
from io import BytesIO

from tests.api.utils.api_client import ApiClient
from tests.api.utils.auth_helper import AuthenticationHelper
from tests.api.utils.booking_data_builder import BookingDataBuilder

"""
Pytest fixtures and hooks for booking API tests

- config → load test configuration from JSON
- auth_token → fetch session-wide authentication token
- api_client → provide ApiClient with base URL and token
- check_health → verify API health (/ping) before tests
- configure_logging → set up logging for test session
- booking_registry → create/delete test bookings from filters.json
- create_test_booking → alias to booking_registry
- pytest_runtest_logreport → collect pass/fail/skip results
- pytest_html_results_summary → embed pie chart in pytest-html report
"""
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
    """Alias to booking_registry for backward compatibility."""
    return booking_registry
    
@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Configure logging for the whole test session"""
    logging.basicConfig(
        level=logging.INFO,  # or DEBUG for more details
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.getLogger().setLevel(logging.INFO)

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


# Track results
results_summary = {"passed": 0, "failed": 0, "skipped": 0}


def pytest_runtest_logreport(report):
    """Hook to collect test results"""
    if report.when == "call":
        if report.passed:
            results_summary["passed"] += 1
        elif report.failed:
            results_summary["failed"] += 1
    elif report.skipped:
        results_summary["skipped"] += 1


def pytest_html_results_summary(prefix, summary, postfix):
    """Hook to add pie chart to pytest-html report"""
    # Prepare pie chart
    labels = list(results_summary.keys())
    sizes = list(results_summary.values())
    colors = ["#28a745", "#dc3545", "#ffc107"]  # green, red, yellow

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
    ax.axis("equal")  # Equal aspect ratio

    # Save to memory
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    # Embed into report
    html = f'<div><h3>📊 Test Results Summary</h3><img src="data:image/png;base64,{encoded}" /></div>'
    prefix.extend([html])
