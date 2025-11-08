from .client import ERLCPyClient

class Logs:
    def __init__(self, client: "ERLCPyClient"):
        self.client = client

    def kill_logs(self):
        return self.client._get("/server/killlogs")

    def command_logs(self):
        return self.client._get("/server/commandlogs")

    def mod_calls(self):
        return self.client._get("/server/modcalls")

    def bans(self):
        return self.client._get("/server/bans")
