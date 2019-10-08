import asyncio

from mpc.common.connection import Connection
from mpc.server._context import Context


class Transport(asyncio.Protocol):

    def __init__(self, hook: Context):
        self.hook = hook
        self.connection = Connection()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        app, method, data = self.connection.unmarshall(data)
        response = self.hook.handle(app, method, **data)
        data = self.connection.marshall(app, method, **response)
        self.transport.write(data)
        self.transport.close()
