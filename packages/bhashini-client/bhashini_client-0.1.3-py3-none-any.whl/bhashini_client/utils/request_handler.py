import requests
import json
from ..config import BASE_URL, DEFAULT_HEADERS

class RequestHandler:
    def __init__(self, api_key: str):
        self.headers = {**DEFAULT_HEADERS, "Authorization": api_key}

    def post(self, payload: dict):
        try:
            response = requests.post(BASE_URL, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
