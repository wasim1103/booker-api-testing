import random
import datetime


class BookingDataBuilder:
    def __init__(self):
        # default valid booking data
        self.firstname = "TestAutomation"
        self.lastname = "User"
        self.totalprice = 150
        self.depositpaid = True
        self.checkin = "2025-09-20"
        self.checkout = "2025-09-25"
        self.additionalneeds = "Breakfast"

    def with_firstname(self, firstname: str):
        self.firstname = firstname
        return self

    def with_lastname(self, lastname: str):
        self.lastname = lastname
        return self

    def with_totalprice(self, price: int):
        self.totalprice = price
        return self

    def with_dates(self, checkin: str, checkout: str):
        self.checkin = checkin
        self.checkout = checkout
        return self

    def with_additionalneeds(self, needs: str):
        self.additionalneeds = needs
        return self

    def build(self) -> dict:
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
