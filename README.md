Booker API Testing
Description
This project is a test automation framework built using Python, Pytest, and Requests to validate the Restful Booker API.
It covers unit-level validations, integration tests, and end-to-end booking lifecycle scenarios (Create → Update → Verify → Delete), ensuring the API behaves as expected.

Features:
✅ Health check validation for API availability
✅ CRUD operation tests for /booking endpoint
✅ Filtering with single & multiple parameters
✅ Retry logic to handle API latency & flaky tests
✅ End-to-end lifecycle validation (Create → Update → Verify → Delete)
✅ HTML and JUnit style reports for CI/CD integration

## Project Structure

```text
booker-api-testing/
├── src/
│   ├── tests/
│   │   ├── api/
│   │   │   ├── booking/
│   │   │   │   ├── test_01_get_booking.py      # Tests for GET bookings with filters
│   │   │   │   ├── test_02_update_booking.py   # Tests for PATCH/PUT booking updates
│   │   │   │   ├── test_03_e2e_booking.py      # End-to-end booking lifecycle tests
│   │   │   └── integration/
│   │   │       └── test_booking_e2e.py         # Integration/E2E scenarios
│   │   └── utils/
│   │       ├── api_client.py                   # API client wrapper
│   │       ├── booking_helper.py               # Helper functions for validation
│   │       ├── booking_data_builder.py         # Dynamic booking payload generator
│   │       └── config.py                       # Configuration (base URL, etc.)
├── requirements.txt                            # Python dependencies
├── pytest.ini                                  # Pytest configuration
└── README.md                                   # Project documentation



Setup Instructions-
1. Clone Repository:
git clone https://github.com/<your-repo>/booker-api-testing.git
cd booker-api-testing

2. Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install Dependencies
pip install -r requirements.txt


Running Tests-
1. Run All Tests
pytest -v

2. Run Specific Test File
pytest src/tests/api/booking/test_01_get_booking.py

3. Run Tests with HTML Report
pytest --html=reports/booker-api-testing-report.html --self-contained-html

4. Run Tests in Parallel
pytest -n auto


Test Reports-
- HTML Report: Generated at reports/booker-api-testing-report.html

Notes:
Default base URL: https://restful-booker.herokuapp.com (configurable in config.py)
Supports both local and CI/CD execution
Retry mechanisms included for flaky tests and booking creation propagation delays
