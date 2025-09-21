📘 Booker API Testing

This project is a test automation framework built using Python, Pytest, and Requests to validate the **Restful Booker API**.

It covers:
- Unit-level validations
- Integration tests
- End-to-end booking lifecycle scenarios (Create → Update → Verify → Delete)

Ensuring the API behaves as expected in different conditions.


✨ Features
- ✅ API Health Checks – Validate the availability of endpoints before running tests.
- ✅ Booking Endpoint Tests (CRUD) – Covers Create, Read, Update, Delete operations for /booking.
- ✅ Bulk Booking Operations – Tests creating/updating/deleting multiple bookings in a single flow.
- ✅ Flexible Filtering – Supports single and multiple filter parameters in GET requests.
- ✅ Retry Logic for Flaky Tests – Automatically retries tests to handle API latency or transient failures.
- ✅ End-to-End Booking Lifecycle Validation – Tests the complete flow: Create → Update → Verify → Delete.
- ✅ Comprehensive Reports – Generates HTML reports with pie chart summary and JUnit-style reports for CI/CD integration.

## Project Structure

```text
booker-api-testing/
├── src/
│   └── tests/                                 # All test code
│       ├── api/
│       │   ├── booking/
│       │   │   ├── test_01_get_booking.py      # Tests for GET bookings with filters
│       │   │   ├── test_02_update_booking.py   # Tests for PATCH booking updates
│       │   │   ├── test_03_delete_booking.py   # Tests for DELETE bookings / end-to-end booking lifecycle
│       │   │
│       │   └── integration/
│       │       └── test_booking_e2e.py        # Integration / E2E booking scenarios
│       │
│       └── utils/
│           ├── api_client.py                  # Wrapper for API requests
│           ├── auth_helper.py                 # Authentication helper functions
│           ├── booking_helper.py              # Validation helper functions
│           └── booking_data_builder.py        # Dynamic payload generator for booking tests
│
├── resources/
│   ├── config/
│   │   └── config.json                        # Environment / API configuration
│   └── test-data/
│       ├── filters.json                        # Test input data for filters
│       └── update_payloads.json               # Test input data for updates
│
├── reports/                                   # Folder to store generated test reports
│   └── booker-api-testing-report.html         # Example pytest-html report
│
├── docker/
│   └── Dockerfile                             # Docker environment setup
│
├── .github/
│   └── workflows/
│       └── api-tests.yml                      # GitHub Actions workflow for CI/CD
│
├── .gitignore                                 # Files/folders to ignore in git
├── pytest.ini                                 # Pytest configuration
├── requirements.txt                           # Python dependencies
└── README.md                                  # Project documentation



Setup Instructions-
1. Clone Repository:
git clone https://github.com/<your-repo>/booker-api-testing.git
cd booker-api-testing

2. Create Virtual Environment
python -m venv venv
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
=> Default base URL: https://restful-booker.herokuapp.com (configurable in config.py)
=> Supports both local and CI/CD execution
=> Retry mechanisms included for flaky tests and booking creation propagation delays
