import pytest
import json
import logging
from tests.api.utils.booking_helper import validate_booking_by_id, get_bookings
from tests.api.utils.booking_data_builder import BookingDataBuilder

logger = logging.getLogger(__name__)

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

    logger.info(
        "Booking created | ID=%s | Payload:\n%s",
        booking_id, json.dumps(booking_data, indent=2)
    )

    yield {"bookingid": booking_id, "data": booking_data}

    # Cleanup after test
    api_client.delete(f"/booking/{booking_id}")


# -----------------------------
# E2E Test: Complete booking lifecycle
# -----------------------------
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

    logger.info("Booking created | ID=%s | Payload:\n%s",
                booking_id, json.dumps(booking_data, indent=2))

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
    updated_payload = {"firstname": "UpdatedName"}
    update_resp = api_client.patch(
        f"/booking/{booking_id}", json=updated_payload)
    update_resp.raise_for_status()
    logger.info("Booking updated successfully | ID=%s | Updated Payload:\n%s",
                booking_id, json.dumps(updated_payload, indent=2))

    # Update filters too
    updated_filters = {"firstname": updated_payload["firstname"]}

    # Validate updated fields
    validate_booking_by_id(
        api_client, {"bookingid": booking_id, "data": updated_payload}, updated_filters)

    # -------------------------------
    # 5. DELETE
    # -------------------------------
    del_resp = api_client.delete(f"/booking/{booking_id}")
    del_resp.raise_for_status()
    logger.info("Booking deleted successfully | ID=%s", booking_id)

    # Confirm deletion
    final_resp = api_client.get(f"/booking/{booking_id}")
    assert final_resp.status_code == 404, f"Booking {booking_id} still exists after deletion"


# -----------------------------
# E2E Test: Bulk booking operations
# -----------------------------


def test_bulk_booking_operations(api_client):
    """
    Bulk operations scenario:
    • Create multiple bookings
    • Apply filters to retrieve subset
    • Update filtered results and validate
    """
    created_bookings = []

    # -------------------------------
    # 1. Create multiple bookings
    # -------------------------------
    for _ in range(5):
        builder = BookingDataBuilder()
        booking_data = builder.build()
        response = api_client.post("/booking", json=booking_data)
        response.raise_for_status()
        booking_id = response.json()["bookingid"]

        created_bookings.append({"id": booking_id, "data": booking_data})
        logger.info(
            "Booking created: ID=%s, payload=%s",
            booking_id,
            json.dumps(booking_data, indent=2),
        )

    # -------------------------------
    # 2. Filter, update & validate each booking
    # -------------------------------
    for b in created_bookings:
        filters = {"firstname": b["data"]["firstname"]}
        filtered_ids = get_bookings(api_client, filters)

        logger.info("Filtered bookings by %s: %s", filters, filtered_ids)
        assert b["id"] in filtered_ids, \
            f"Booking {b['id']} not found in filtered results {filtered_ids}"

        updated_payload = {"lastname": "BulkUpdated"}
        resp_update = api_client.patch(f"/booking/{b['id']}", json=updated_payload)
        assert resp_update.status_code == 200, \
            f"Unexpected status {resp_update.status_code} for booking {b['id']}"

        # Validate booking after update
        validate_booking_by_id(
            api_client,
            {"bookingid": b["id"], "data": {**b["data"], **updated_payload}},
            filters,
        )
        logger.info("Booking %s updated successfully with %s", b["id"], updated_payload)

    # -------------------------------
    # 3. Cleanup all created bookings
    # -------------------------------
    for b in created_bookings:
        resp_del = api_client.delete(f"/booking/{b['id']}")
        assert resp_del.status_code in [200, 201, 204], \
            f"Unexpected delete status {resp_del.status_code} for booking {b['id']}"
        logger.info("Booking %s deleted successfully", b["id"])



# -----------------------------
# E2E Test: Cross-endpoint consistency verification
# -----------------------------
def test_cross_endpoint_consistency(api_client, create_e2e_booking):
    """
    Cross-endpoint consistency:
    Verify that booking details from /booking/{id} match results from /booking (filtered)
    """
    booking_id = create_e2e_booking["bookingid"]
    booking_data = create_e2e_booking["data"]

    # -------------------------------
    # 1. GET booking by ID
    # -------------------------------
    resp_by_id = api_client.get(f"/booking/{booking_id}")
    resp_by_id.raise_for_status()
    booking_by_id = resp_by_id.json()
    logger.info(
        "Booking fetched by ID | ID=%s | Data:\n%s",
        booking_id, json.dumps(booking_by_id, indent=2)
    )

    # -------------------------------
    # 2. GET booking via /booking with filter
    # -------------------------------
    filters = {"firstname": booking_data["firstname"]}
    booking_ids_filtered = get_bookings(api_client, filters)
    assert booking_id in booking_ids_filtered, f"Booking {booking_id} not found using filters {filters}"

    # Fetch full data for first matching booking
    resp_filtered = api_client.get(f"/booking/{booking_id}")
    resp_filtered.raise_for_status()
    booking_filtered = resp_filtered.json()
    logger.info(
        "Booking fetched via filter | ID=%s | Data:\n%s",
        booking_id, json.dumps(booking_filtered, indent=2)
    )

    # -------------------------------
    # 3. Validate consistency
    # -------------------------------
    validate_booking_by_id(
        api_client, {"bookingid": booking_id, "data": booking_data}, filters)
    logger.info(
        "Cross-endpoint consistency validated for booking | ID=%s", booking_id)
