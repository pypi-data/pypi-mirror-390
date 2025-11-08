from .client import ERLCPyClient
from .server import Server
from .players import Players
from .logs import Logs
from .vehicles import Vehicles

class ERLCPy:
    def __init__(self, server_key: str):
        self.client = ERLCPyClient(server_key)
        self.server = Server(self.client)
        self.players = Players(self.client)
        self.logs = Logs(self.client)
        self.vehicles = Vehicles(self.client)
