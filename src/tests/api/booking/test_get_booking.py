import pytest
import json
import time
from tests.api.utils.booking_helper import validate_booking_by_id, get_bookings

# Load test data's from JSON
with open("resources/test-data/filters.json") as f:
    filter_data = json.load(f)



@pytest.mark.parametrize("data", [d for d in filter_data if d["description"] == "No filters"])
def test_Retrieve_all_booking_IDs_without_filters(api_client, create_test_booking, data):
    response = api_client.get("/booking")
    assert response.status_code == 200
    booking_ids = response.json()

    assert isinstance(booking_ids, list), f"Response is not a list"
    assert len(booking_ids) > 0, f"Response is having zero booking"

    ids = [item["bookingid"] for item in booking_ids]
    # Check that every bookingid is a number
    assert all(isinstance(bid, int) for bid in ids), f"Not all booking IDs are numbers: {ids}"
    print(f"Found booking IDs: {ids}")

    assert create_test_booking["bookingid"] in ids, f"Booking ID{create_test_booking["bookingid"]} not found"


@pytest.mark.parametrize(
    "data",
    [d for d in filter_data if d["description"] == "Individual filter"],
    ids=lambda d: f"{d['description']}-{d['params']}"
)
def test_by_applying_single_filters(api_client, create_test_booking, data):
    """Test Individual filters by applying firstname, lastname, checkin, checkout"""
    # 1. Validate ID presence with GET /booking (filtered)
    ids = get_bookings(api_client, data["params"])
    assert create_test_booking["bookingid"] in ids

    # 2. Validate payload with GET /booking/{id}
    validate_booking_by_id(api_client, create_test_booking, data["params"])
    
    
@pytest.mark.parametrize(
    "data",
    [d for d in filter_data if d["description"] == "Multiple filters"],
    ids=lambda d: f"{d['description']}-{d['params']}"
)
def test_by_applying_multiple_filters(api_client, create_test_booking, data):
    """Test Multiple filters by firstname, lastname, checkin, checkout"""    
    ids = get_bookings(api_client, data["params"])
    assert create_test_booking["bookingid"] in ids

    validate_booking_by_id(api_client, create_test_booking, data["params"])


@pytest.mark.parametrize(
        "data", 
        [d for d in filter_data if d["description"] == "Invalid Value Format In filter"], 
        ids=lambda d: f"{d['description']}-{d['params']}"
)
def test_Validate_error_handling(api_client, data):
    """Test invalid filters return proper error responses"""
    response = api_client.get("/booking", params=data["params"])

    print(f"\nRequest: GET /booking, params={data['params']}")
    print(f"Response status: {response.status_code}")
    # print(f"Response body: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == data["expected_status"]


def test_get_booking_performance(api_client):
    """Basic performance validation: Response time < 2 seconds"""
    start = time.time()
    response = api_client.get("/booking")
    elapsed = time.time() - start

    print("\nPerformance test: GET /booking (no filters)")
    print(f"Response status: {response.status_code}, Time taken: {elapsed:.2f}s")

    assert response.status_code == 200
    assert elapsed < 2
