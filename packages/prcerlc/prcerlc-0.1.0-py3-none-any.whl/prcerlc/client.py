import requests

class ERLCPyClient:
    BASE_URL = "https://api.policeroleplay.community/v1"

    def __init__(self, server_key: str):
        self.session = requests.Session()
        self.session.headers.update({
            "server-key": server_key,
            "Accept": "application/json"
        })

    def _get(self, path: str, params=None):
        url = f"{self.BASE_URL}{path}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, data=None):
        url = f"{self.BASE_URL}{path}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json() if response.content else None
