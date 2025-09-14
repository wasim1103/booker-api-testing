import pytest
import requests

def post_healthcheck():
    resp = requests.get("https://restful-booker.herokuapp.com/ping")
    print(resp.status_code)


post_healthcheck()