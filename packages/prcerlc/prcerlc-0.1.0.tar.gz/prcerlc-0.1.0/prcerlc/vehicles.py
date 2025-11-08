from .client import ERLCPyClient

class Vehicles:
    def __init__(self, client: "ERLCPyClient"):
        self.client = client

    def list(self):
        return self.client._get("/server/vehicles")
