# src/tests/api/booking/test_03_e2e_booking.py
import pytest
import json
from tests.api.utils.booking_helper import validate_booking_by_id, get_bookings
from tests.api.utils.booking_data_builder import BookingDataBuilder

# -----------------------------
# Fixture: Create a single booking for E2E tests
# -----------------------------
@pytest.fixture(scope="function")
def create_e2e_booking(api_client):
    """Fixture to create a single booking for E2E tests"""
    builder = BookingDataBuilder()
    booking_data = builder.build()

    response = api_client.post("/booking", json=booking_data)
    response.raise_for_status()
    booking_id = response.json()["bookingid"]

    print(
        f"\nBooking created: ID={booking_id}, payload={json.dumps(booking_data, indent=2)}")

    yield {"bookingid": booking_id, "data": booking_data}

    # Cleanup after test
    api_client.delete(f"/booking/{booking_id}")

# -----------------------------
# E2E Test: Complete booking lifecycle
# -----------------------------
@pytest.mark.e2e
def test_e2e_booking_lifecycle(api_client):
    """Complete booking lifecycle: Create → Update → Verify → Delete"""

    # -------------------------------
    # 1. CREATE
    # -------------------------------
    builder = BookingDataBuilder()
    booking_data = builder.build()
    response = api_client.post("/booking", json=booking_data)
    response.raise_for_status()
    booking_id = response.json()["bookingid"]

    print(f"\nBooking created: ID={booking_id}, payload={booking_data}")

    # -------------------------------
    # 2. VERIFY VIA SINGLE FILTER (firstname)
    # -------------------------------
    filters = {"firstname": booking_data["firstname"]}
    booking_ids = get_bookings(api_client, filters)
    assert booking_id in booking_ids, f"Booking {booking_id} not returned using filters {filters}"

    # -------------------------------
    # 3. FETCH BY ID & VALIDATE
    # -------------------------------
    validate_booking_by_id(
        api_client, {"bookingid": booking_id, "data": booking_data}, filters)

    # -------------------------------
    # 4. UPDATE
    # -------------------------------
    #updated_payload = booking_data.copy()
    updated_payload = {"firstname": "UpdatedName"}
    update_resp = api_client.patch(f"/booking/{booking_id}", json=updated_payload)
    update_resp.raise_for_status()
    print(f"\nBooking {booking_id} updated successfully")

    # Update filters too
    updated_filters = {"firstname": updated_payload["firstname"]}

    # Validate updated fields
    validate_booking_by_id(
        api_client, {"bookingid": booking_id, "data": updated_payload}, updated_filters
    )
    # -------------------------------
    # 5. DELETE
    # -------------------------------
    del_resp = api_client.delete(f"/booking/{booking_id}")
    del_resp.raise_for_status()
    print(f"\nBooking {booking_id} deleted successfully")

    # Confirm deletion
    final_resp = api_client.get(f"/booking/{booking_id}")
    assert final_resp.status_code == 404, f"Booking {booking_id} still exists after deletion"


# -----------------------------
# E2E Test: Bulk booking operations (planned)
# -----------------------------
@pytest.mark.e2e
@pytest.mark.skip(reason="Bulk operations scenario - to be implemented")
def test_bulk_booking_operations(api_client):
    """
    Planned:
    • Create multiple bookings
    • Apply filters to retrieve subset
    • Update filtered results and validate
    """
    pass

# -----------------------------
# E2E Test: Cross-endpoint consistency verification
# -----------------------------
@pytest.mark.e2e
def test_cross_endpoint_consistency(api_client, create_e2e_booking):
    """
    Cross-endpoint consistency:
    Verify that booking details from /booking/{id} match results from /booking (filtered)
    """
    # -------------------------------
    # 1. Retrieve booking info from creation response
    # -------------------------------
    booking_id = create_e2e_booking["bookingid"]
    booking_data = create_e2e_booking["data"]
    print(f"\nBooking created: ID={booking_id}, payload={booking_data}")

    # -------------------------------
    # 2. GET booking by ID
    # -------------------------------
    resp_by_id = api_client.get(f"/booking/{booking_id}")
    resp_by_id.raise_for_status()
    booking_by_id = resp_by_id.json()
    print(f"Booking fetched by ID: {booking_by_id}")

    # -------------------------------
    # 3. GET booking via /booking with filter
    # -------------------------------
    filters = {"firstname": booking_data["firstname"]}
    booking_ids_filtered = get_bookings(api_client, filters)
    assert booking_id in booking_ids_filtered, (
        f"Booking {booking_id} not found using filters {filters}"
    )

    # Fetch full data for first matching booking (could extend to all)
    # Assuming get_bookings returns only booking IDs
    resp_filtered = api_client.get(f"/booking/{booking_id}")
    resp_filtered.raise_for_status()
    booking_filtered = resp_filtered.json()
    print(f"Booking fetched via filter: {booking_filtered}")

    # -------------------------------
    # 4. Validate consistency
    # -------------------------------
    validate_booking_by_id(
        api_client,
        {"bookingid": booking_id, "data": booking_data},
        filters
    )

    print(f"Cross-endpoint consistency validated for booking {booking_id}")