import pytest

# -----------------------------
# Successful deletion of a booking
# -----------------------------
def test_successful_delete_and_verify(api_client, create_test_booking):
    """Successfully delete existing booking and verify GET returns 404"""
    # Pick the first booking from the registry
    booking_id = create_test_booking.pop(0)["bookingid"]

    # Delete the booking
    response = api_client.delete(f"/booking/{booking_id}")
    print("Delete Response:", response.status_code, response.text)
    assert response.status_code == 201, "Expected 201 on successful delete"

    # Verify booking is no longer retrievable
    get_response = api_client.get(f"/booking/{booking_id}")
    print("Get Booking post delete Response:", get_response.status_code, get_response.text)
    assert get_response.status_code == 404, "Booking should not be found after deletion"


# -----------------------------
# Deleting non-existent booking IDs
# -----------------------------
@pytest.mark.parametrize(
    "invalid_id", ["99999999", "-1", "abc"],  # non-existent or invalid IDs
    ids=["non-existent-id", "negative-id", "string-id"]
)
def test_delete_non_existent_booking(api_client, invalid_id):
    """Deleting non-existent booking IDs should return 404 or 400 or 405"""
    response = api_client.delete(f"/booking/{invalid_id}")
    print("Delete Response for invalid_id:", invalid_id, response.status_code, response.text)
    assert response.status_code in [400, 404, 405]


# -----------------------------
# Deleting a booking with invalid or missing auth
# -----------------------------
@pytest.mark.parametrize(
    "auth_header",
    [
        {"Authorization": "Bearer invalidtoken"},
        {},  # missing auth
    ],
    ids=["invalid-auth", "missing-auth"],
)
def test_delete_with_invalid_auth(api_client, create_test_booking, auth_header):
    booking_id = create_test_booking[0]["bookingid"]

    response = api_client.delete(f"/booking/{booking_id}", headers=auth_header)
    print(f"Delete Response with auth {auth_header}: {response.status_code}, {response.text}")
    assert response.status_code in [401, 403, 405]


# -----------------------------
# Idempotent deletion of the same booking
# -----------------------------
def test_idempotent_delete(api_client, create_test_booking):
    """Deleting same booking twice should result in 201 then 404"""
    booking_id = create_test_booking.pop(0)["bookingid"]

    # First delete attempt
    first = api_client.delete(f"/booking/{booking_id}")
    print("First delete:", first.status_code, first.text)
    assert first.status_code == 201

    # Second delete attempt
    second = api_client.delete(f"/booking/{booking_id}")
    print("Second delete:", second.status_code, second.text)
    assert second.status_code in [404, 405]


# -----------------------------
# Concurrent deletion of the same booking
# -----------------------------
def test_concurrent_delete(api_client, create_test_booking):
    """Concurrent deletion should be handled gracefully"""
    booking_id = create_test_booking.pop(0)["bookingid"]

    # Fire two delete requests back-to-back
    resp1 = api_client.delete(f"/booking/{booking_id}")
    resp2 = api_client.delete(f"/booking/{booking_id}")

    print("Concurrent delete responses:", resp1.status_code, resp2.status_code)

    # One should succeed (201), other should return not found (404)
    statuses = sorted([resp1.status_code, resp2.status_code])
    assert statuses == [201, 404], f"Concurrent DELETE returned unexpected statuses: {statuses}"
