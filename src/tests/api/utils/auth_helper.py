import requests

class AuthenticationHelper:
    @staticmethod
    def get_token(base_url, username, password):
        url = f"{base_url}/auth"
        payload = {"username": username, "password": password}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("token")
