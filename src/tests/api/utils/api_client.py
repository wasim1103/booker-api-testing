# src/tests/api/utils/api_client.py
import requests


class ApiClient:
    def __init__(self, base_url, auth_token=None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            # Booker API expects token as cookie
            headers["Cookie"] = f"token={self.auth_token}"
        return headers

    # GET request
    def get(self, endpoint, params=None):
        return requests.get(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            params=params
        )

    # POST request
    def post(self, endpoint, data=None, json=None):
        return requests.post(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            data=data,
            json=json
        )

    # PATCH request
    def patch(self, endpoint, data=None, json=None):
        return requests.patch(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            data=data,
            json=json
        )

    # PUT request (optional, for full updates)
    def put(self, endpoint, data=None, json=None):
        return requests.put(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            data=data,
            json=json
        )

    # DELETE request
    def delete(self, endpoint, headers=None):
        final_headers = self._headers()
        if headers:
            final_headers.update(headers)
        return requests.delete(
            f"{self.base_url}{endpoint}",
            headers=final_headers
        )
