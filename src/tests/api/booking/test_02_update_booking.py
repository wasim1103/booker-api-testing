import pytest
import json
from datetime import datetime
from tests.api.utils.booking_helper import validate_updated_fields, validate_unchanged_fields

# Load update scenarios from JSON
with open("resources/test-data/update_payloads.json") as f:
    update_data = json.load(f)

# -----------------------------
# Update individual booking field with type validation
# -----------------------------
@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] == "Update Individual Field"],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_individual_field_update_with_type_validation(api_client, create_test_booking, data):
    """Test individual field updates with type validation"""
    booking_to_test = create_test_booking[0]
    booking_id = booking_to_test["bookingid"]

    payload = data["payload"]

    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:\n", json.dumps(original, indent=2))

    response = api_client.patch(f"/booking/{booking_id}", json=payload)
    assert response.status_code == 200, f"Unexpected status {response.status_code} for payload {payload}"

    updated = response.json()
    print("Updated booking:\n", json.dumps(updated, indent=2))

    # Type validation
    assert isinstance(updated["firstname"], str)
    assert isinstance(updated["lastname"], str)
    assert isinstance(updated["totalprice"], int)
    assert isinstance(updated["depositpaid"], bool)
    assert isinstance(updated["bookingdates"], dict)
    for d in ["checkin", "checkout"]:
        datetime.strptime(updated["bookingdates"][d], "%Y-%m-%d")
    assert isinstance(updated.get("additionalneeds", ""), str)

    # Validate updated fields
    validate_updated_fields(updated, payload)

# -----------------------------
# Update multiple booking fields
# -----------------------------
@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] in ["Update Multiple Fields"]],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_multiple_fields_get_updated(api_client, create_test_booking, data):
    """Test multiple field updates"""
    booking_to_test = create_test_booking[0]
    booking_id = booking_to_test["bookingid"]

    payload = data["payload"]

    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:\n", json.dumps(original, indent=2))

    response = api_client.patch(f"/booking/{booking_id}", json=payload)
    assert response.status_code == 200, f"Unexpected status {response.status_code} for payload {payload}"

    updated = api_client.get(f"/booking/{booking_id}").json()
    print("Updated booking:\n", json.dumps(updated, indent=2))

    validate_updated_fields(updated, payload)

# -----------------------------
# Verify non-updated fields remain unchanged
# -----------------------------
def test_non_updated_field_remains_unchanged(api_client, create_test_booking):
    """Verify that fields not updated remain unchanged"""
    booking_to_test = create_test_booking[0]
    booking_id = booking_to_test["bookingid"]

    original = api_client.get(f"/booking/{booking_id}").json()
    print("Original booking:", original)

    payload = {"firstname": "CheckUnchanged"}
    response = api_client.patch(f"/booking/{booking_id}", json=payload)
    assert response.status_code == 200

    updated = response.json()
    print("Updated booking:", updated)

    validate_updated_fields(updated, payload)
    validate_unchanged_fields(original, updated, exclude=["firstname"])

# -----------------------------
# Error handling for invalid booking updates
# -----------------------------
@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d["description"] == "Invalid Value Format In Update"],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_validate_error_handling(api_client, create_test_booking, data):
    """Verify API returns correct errors for invalid updates"""
    booking_to_test = create_test_booking[0]
    booking_id = booking_to_test["bookingid"]
    endpoint_id = data.get("invalid_id", booking_id)

    client = api_client if data.get("auth") != "none" else api_client.__class__(api_client.base_url)

    response = client.patch(f"/booking/{endpoint_id}", json=data["payload"])
    print("Booking ID:", endpoint_id)
    print("Payload sent:", data["payload"])
    print("Status:", response.status_code)
    print("Text:", response.text)

    assert response.status_code in [400, 404, 422, 401, 403], f"Unexpected status {response.status_code} for invalid case {data['description']}"
  

# -----------------------------
# Verify idempotency of PATCH updates
# -----------------------------
@pytest.mark.parametrize(
    "data",
    [d for d in update_data if d.get("idempotent")],
    ids=lambda d: f"{d['description']}-{d['payload']}"
)
def test_idempotency_of_updates(api_client, create_test_booking, data):
    """Verify PATCH requests are idempotent"""
    booking_to_test = create_test_booking[0]
    booking_id = booking_to_test["bookingid"]

    payload = data["payload"]

    first = api_client.patch(f"/booking/{booking_id}", json=payload)
    second = api_client.patch(f"/booking/{booking_id}", json=payload)

    print("Booking ID:", booking_id)
    print("Payload:", payload)
    print("First status:", first.status_code, "Second status:", second.status_code)
    print("First response:", first.text, "Second response:", second.text)

    # Idempotent update → always expect 200
    assert first.status_code == 200, f"First PATCH returned {first.status_code} unexpectedly"
    assert second.status_code == 200, f"Second PATCH returned {second.status_code} unexpectedly"

    # The response body should be identical for both PATCH calls
    assert first.json() == second.json(), "PATCH responses are not identical for idempotent update"
