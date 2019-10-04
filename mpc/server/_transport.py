import asyncio

from mpc.server._connection import Connection
from mpc.server._events import EventHook


class Transport(asyncio.Protocol):

    def __init__(self, hook: EventHook):
        self.hook = hook
        self.connection = Connection()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        app, method, data = self.connection.unmarshall(data)
        response = self.hook.handle(app, method, **data)
        data = self.connection.marshall(app, method, **response)
        self.send_response(data)
        self.transport.close()

    def send_response(self, data):
        self.transport.write(data)
