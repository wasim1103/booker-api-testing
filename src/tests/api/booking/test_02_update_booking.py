import pytest
import json
from datetime import datetime
from tests.api.utils.booking_helper import validate_updated_fields, validate_unchanged_fields


# Load update scenarios from JSON
with open("resources/test-data/update_payloads.json") as f:
    update_data = json.load(f)

# Parametrize test using update data where description is "Update Individual Field"
# This test ensures that individual fields are updated correctly and type validation passes
# The ids lambda provides readable test case identifiers in pytest reports
@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] == "Update Individual Field"],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_individual_field_update_with_type_validation(api_client, create_test_booking, data):
    # Loop through dynamically created bookings for this test session
    for booking in create_test_booking:
        booking_id = booking["bookingid"]

    # Prepare the PATCH request body using the payload defined in the test scenario
    payload = data["payload"]

    # Fetch original booking for debug/logging
    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:\n", json.dumps(original, indent=2))

    # Perform PATCH update
    response = api_client.patch(f"/booking/{booking_id}", json=payload)
    assert response.status_code == data["expected_status"], f"Unexpected status {response.status_code}"

    updated = response.json()
    print("Updated booking:\n", json.dumps(updated, indent=2))
    
    # Validate types of all fields
    assert isinstance(updated["firstname"], str), "firstname should be string"
    assert isinstance(updated["lastname"], str), "lastname should be string"
    assert isinstance(updated["totalprice"], int), "totalprice should be integer"
    assert isinstance(updated["depositpaid"], bool), "depositpaid should be boolean"
    assert isinstance(updated["bookingdates"], dict), "bookingdates should be object"

    # Validate checkin/checkout as proper dates
    for d in ["checkin", "checkout"]:
        try:
            datetime.strptime(updated["bookingdates"][d], "%Y-%m-%d")
        except ValueError:
            pytest.fail(f"{d} is not a valid date: {updated['bookingdates'][d]}")

    assert isinstance(updated.get("additionalneeds", ""), str), "additionalneeds should be string if present"

    # Validate updated field values
    validate_updated_fields(updated, payload)

# Parametrize test using update data where description is "Update Multiple Fields"
# This test ensures that multiple fields are updated correctly and persisted
# The ids lambda provides readable test case identifiers in pytest reports
@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] in ["Update Multiple Fields"]],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_multiple_fields_get_updated(api_client, create_test_booking, data):
    # Loop through dynamically created bookings for this test session
    for booking in create_test_booking:
        booking_id = booking["bookingid"]

    # Prepare the PATCH request body using the payload defined in the test scenario        
    payload = data["payload"]

    # Fetch original booking to compare updates and for logging
    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:\n", json.dumps(original, indent=2))

    # Perform PATCH update
    response = api_client.patch(f"/booking/{booking_id}", json=payload)
    assert response.status_code == data["expected_status"]

    # Fetch updated booking after PATCH
    updated = api_client.get(f"/booking/{booking_id}").json()
    print("Updated booking:\n", json.dumps(updated, indent=2))

    # Validate updated fields
    validate_updated_fields(updated, payload)   
  

# Test non-updated fields remain unchanged
# This test ensures that fields not part of the PATCH payload are not modified
def test_non_updated_field_remains_unchanged(api_client, create_test_booking):
    # Loop through dynamically created bookings for this test session
    for booking in create_test_booking:
        booking_id = booking["bookingid"]

    # Get original booking
    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:", original)

    # Update only firstname
    payload = {"firstname": "CheckUnchanged"}
    response = api_client.patch(f"/booking/{booking_id}", json=payload)
    assert response.status_code == 200

    # Fetch updated booking
    updated = response.json()
    print("Updated booking:", updated)

    # Validate updated fields
    validate_updated_fields(updated, payload)

    # non-updated field should remain same
    validate_unchanged_fields(original, updated, exclude=["firstname"])


# Parametrize test using update data where description is "Invalid Value Format In Update"
# This test ensures the API returns proper error responses for invalid update payloads
# The ids lambda provides readable test case identifiers in pytest reports        
@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] == "Invalid Value Format In Update"],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_validate_error_handling(api_client, create_test_booking, data):
    # Loop through dynamically created bookings for this test session
    for booking in create_test_booking:
        booking_id = booking["bookingid"]
    endpoint_id = data.get("invalid_id", booking_id)

    # Choose API client based on auth requirement
    if data.get("auth") == "none":
        from tests.api.utils.api_client import ApiClient
        client = ApiClient(api_client.base_url)
    else:
        client = api_client

    # Send PATCH request
    response = client.patch(f"/booking/{endpoint_id}", json=data["payload"])
    print("Booking ID:", endpoint_id)
    print("Payload sent:", data["payload"])
    print("Status:", response.status_code)
    print("Text:", response.text)

    # Assert expected error status or common forbidden/method errors
    assert response.status_code == data["expected_status"] or response.status_code in [403, 405]

# Parametrize test using update data where idempotent is True
# This test ensures PATCH requests are idempotent, i.e., repeated updates produce same result
# The ids lambda provides readable test case identifiers in pytest reports
@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d.get("idempotent")],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_idempotency_of_updates(api_client, create_test_booking, data):
    # Loop through dynamically created bookings for this test session
    for booking in create_test_booking:
        booking_id = booking["bookingid"]
        
    # Prepare the PATCH request body using the payload defined in the test scenario    
    payload = data["payload"]

    # First PATCH request
    first = api_client.patch(f"/booking/{booking_id}", json=payload)
    print("Booking ID:", booking_id)
    print("Payload sent:", payload)
    print("First Update status:", first.status_code)
    print("First Update Text:", first.text)

    # Second PATCH request to test idempotency
    second = api_client.patch(f"/booking/{booking_id}", json=payload)   
    print("Second Update status:", second.status_code)
    print("Second Update Text:", second.text)

    # Assert both updates have expected status
    assert first.status_code == data["expected_status"]
    assert second.status_code == data["expected_status"]

    # Assert both updates return identical payloads
    assert first.json() == second.json()
