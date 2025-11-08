from .client import ERLCPyClient

class Server:
    def __init__(self, client: "ERLCPyClient"):
        self.client = client

    def status(self):
        return self.client._get("/server")

    def run_command(self, command: str):
        return self.client._post("/server/command", {"command": command})
