import pytest
import json
from datetime import datetime
from tests.api.utils.booking_helper import validate_updated_fields, validate_unchanged_fields


# Load update scenarios from JSON
with open("resources/test-data/update_payloads.json") as f:
    update_data = json.load(f)

@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] == "Update Individual Field"],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_individual_field_update_with_type_validation(api_client, create_test_booking, data):
    booking_id = create_test_booking["bookingid"]
    payload = data["payload"]

    # Fetch original booking for debug/logging
    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:\n", json.dumps(original, indent=2))

    # Perform PATCH update
    response = api_client.patch(f"/booking/{booking_id}", data=payload)
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

    # Validate updated fields
    validate_updated_fields(updated, payload)


@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] in ["Update Multiple Fields"]],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_multiple_fields_get_updated(api_client, create_test_booking, data):
    booking_id = create_test_booking["bookingid"]
    payload = data["payload"]

    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:\n", json.dumps(original, indent=2))

    response = api_client.patch(f"/booking/{booking_id}", data=payload)
    assert response.status_code == data["expected_status"]

    updated = api_client.get(f"/booking/{booking_id}").json()
    print("Updated booking:\n", json.dumps(updated, indent=2))

    # Validate updated fields
    validate_updated_fields(updated, payload)   
  

def test_non_updated_field_remains_unchanged(api_client, create_test_booking):
    booking_id = create_test_booking["bookingid"]

    # Get original booking
    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:", original)

    # Update only firstname
    payload = {"firstname": "CheckUnchanged"}
    response = api_client.patch(f"/booking/{booking_id}", data=payload)
    assert response.status_code == 200

    updated = response.json()
    print("Updated booking:", updated)

    # Validate updated fields
    validate_updated_fields(updated, payload)

    # non-updated field should remain same
    validate_unchanged_fields(original, updated, exclude=["firstname"])
        

@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] == "Invalid Value Format In Update"],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_validate_error_handling(api_client, create_test_booking, data):
    booking_id = create_test_booking["bookingid"]
    endpoint_id = data.get("invalid_id", booking_id)

    # Handle missing auth
    if data.get("auth") == "none":
        from tests.api.utils.api_client import ApiClient
        client = ApiClient(api_client.base_url)
    else:
        client = api_client

    response = client.patch(f"/booking/{endpoint_id}", data=data["payload"])
    print("Booking ID:", endpoint_id)
    print("Payload sent:", data["payload"])
    print("Status:", response.status_code)
    print("Text:", response.text)
    assert response.status_code == data["expected_status"] or response.status_code in [403, 405]


@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d.get("idempotent")],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_idempotency_of_updates(api_client, create_test_booking, data):
    booking_id = create_test_booking["bookingid"]
    payload = data["payload"]

    first = api_client.patch(f"/booking/{booking_id}", data=payload)
    print("Booking ID:", booking_id)
    print("Payload sent:", payload)
    print("First Update status:", first.status_code)
    print("First Update Text:", first.text)

    second = api_client.patch(f"/booking/{booking_id}", data=payload)   
    print("Second Update status:", second.status_code)
    print("Second Update Text:", second.text)

    assert first.status_code == data["expected_status"]
    assert second.status_code == data["expected_status"]
    assert first.json() == second.json()
