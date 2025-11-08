from .client import ERLCPyClient

class Players:
    def __init__(self, client: "ERLCPyClient"):
        self.client = client

    def list(self):
        return self.client._get("/server/players")

    def join_logs(self):
        return self.client._get("/server/joinlogs")

    def queue(self):
        return self.client._get("/server/queue")
