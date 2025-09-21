from faker import Faker
from datetime import timedelta, datetime
import random

faker = Faker()

"""
BookingDataBuilder class

Generates dynamic booking payloads for testing.
- Uses Faker to create realistic defaults (names, dates, prices).
- Supports overriding fields with custom params (e.g., from filters.json).
- Provides `build()` to return final booking dictionary.
"""
class BookingDataBuilder:
    def __init__(self, params: dict = None):
        """
        Initialize booking with dynamic defaults using Faker.
        If `params` is provided, override defaults with those values.
        """
        # Dynamic defaults
        self.firstname = faker.first_name()
        self.lastname = faker.last_name()
        self.totalprice = random.randint(50, 500)
        self.depositpaid = random.choice([True, False])

        # Generate future check-in/check-out dates
        checkin_date = faker.date_between(start_date="today", end_date="+30d")
        checkout_date = checkin_date + timedelta(days=random.randint(1, 7))
        self.checkin = checkin_date.strftime("%Y-%m-%d")
        self.checkout = checkout_date.strftime("%Y-%m-%d")

        self.additionalneeds = random.choice(
            ["Breakfast", "Lunch", "Dinner", "None"])

        # Override defaults with params from filters.json
        if params:
            self._apply_params(params)

    def _apply_params(self, params: dict):
        """Override defaults with values from filters.json entry"""
        if "firstname" in params:
            self.firstname = str(params["firstname"])
        if "lastname" in params:
            self.lastname = str(params["lastname"])
        if "totalprice" in params:
            self.totalprice = int(params["totalprice"])
        if "depositpaid" in params:
            self.depositpaid = bool(params["depositpaid"])
        if "checkin" in params:
            self.checkin = str(params["checkin"])
        if "checkout" in params:
            self.checkout = str(params["checkout"])
        if "additionalneeds" in params:
            self.additionalneeds = str(params["additionalneeds"])

    def build(self) -> dict:
        """Return the final booking payload"""
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "totalprice": self.totalprice,
            "depositpaid": self.depositpaid,
            "bookingdates": {
                "checkin": self.checkin,
                "checkout": self.checkout
            },
            "additionalneeds": self.additionalneeds
        }
