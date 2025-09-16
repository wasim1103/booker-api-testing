# src/tests/api/utils/api_client.py
import requests

class ApiClient:
    def __init__(self, base_url, auth_token=None):
        self.base_url = base_url
        self.auth_token = auth_token

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Cookie"] = f"token={self.auth_token}"  # Booker API expects token as cookie
        return headers

    def get(self, endpoint, params=None):
        return requests.get(f"{self.base_url}{endpoint}", headers=self._headers(), params=params)

    def post(self, endpoint, data=None):
        return requests.post(f"{self.base_url}{endpoint}", headers=self._headers(), json=data)

    def patch(self, endpoint, data=None):
        return requests.patch(f"{self.base_url}{endpoint}", headers=self._headers(), json=data)

    def delete(self, endpoint, headers=None):
        final_headers = self._headers()
        if headers:  # merge custom headers (e.g., invalid/missing auth)
            final_headers.update(headers)
        return requests.delete(f"{self.base_url}{endpoint}", headers=final_headers)
