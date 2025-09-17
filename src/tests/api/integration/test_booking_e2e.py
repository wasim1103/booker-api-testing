# src/tests/api/booking/test_03_e2e_booking.py
import pytest
import json
from tests.api.utils.booking_helper import validate_booking_by_id, get_bookings
from tests.api.utils.booking_data_builder import BookingDataBuilder


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


@pytest.mark.e2e
def test_e2e_booking_lifecycle(api_client):
    """Complete booking lifecycle: Create → Update → Verify → Delete"""
    from tests.api.utils.booking_data_builder import BookingDataBuilder

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


@pytest.mark.e2e
@pytest.mark.skip(reason="Cross-endpoint consistency verification - to be implemented")
def test_cross_endpoint_consistency(api_client):
    """
    Planned:
    • Verify booking details from multiple endpoints remain consistent
    • Example: booking details from /booking/{id} should match filtered results from /booking
    """
    pass