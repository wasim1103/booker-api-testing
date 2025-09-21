import requests

"""
ApiClient class

Wrapper around `requests` to simplify API calls.
- Handles base URL and auth token (as Cookie).
- Provides helper methods: GET, POST, PATCH, PUT, DELETE.
"""
class ApiClient:
    def __init__(self, base_url, auth_token=None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token

    def _headers(self):
        """Build default headers (adds Cookie if auth_token is set)."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            # Booker API expects token as cookie
            headers["Cookie"] = f"token={self.auth_token}"
        return headers

    # GET request
    def get(self, endpoint, params=None):
        """Send GET request with optional query parameters."""
        return requests.get(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            params=params
        )

    # POST request
    def post(self, endpoint, data=None, json=None):
        """Send POST request with data or JSON payload."""
        return requests.post(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            data=data,
            json=json
        )

    # PATCH request
    def patch(self, endpoint, data=None, json=None):
        """Send PATCH request for partial updates."""
        return requests.patch(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            data=data,
            json=json
        )

    # PUT request (optional, for full updates)
    def put(self, endpoint, data=None, json=None):
        """Send PUT request for full updates/replacements."""
        return requests.put(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            data=data,
            json=json
        )

    # DELETE request
    def delete(self, endpoint, headers=None):
        """Send DELETE request with optional custom headers."""
        final_headers = self._headers()
        if headers:
            final_headers.update(headers)
        return requests.delete(
            f"{self.base_url}{endpoint}",
            headers=final_headers
        )
