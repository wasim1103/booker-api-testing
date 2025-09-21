import requests
"""
AuthenticationHelper class

Utility for handling authentication.
- Provides method to fetch auth token from API.
"""
class AuthenticationHelper:
    @staticmethod    
    def get_token(base_url, username, password):
        """Send credentials to /auth endpoint and return token."""
        url = f"{base_url}/auth"
        payload = {"username": username, "password": password}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("token")
