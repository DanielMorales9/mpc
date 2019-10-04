import asyncio

from mpc.server._connection import Connection


class Client(object):

    def __init__(self):
        self.connection = Connection()
        self.loop = asyncio.get_event_loop()
        self.reader = None
        self.writer = None

    async def connect(self, host, port):
        self.reader, self.writer = await asyncio.open_connection(host, port, loop=self.loop)

    def send(self, *args, **kwargs):
        message = self.connection.marshall(*args, **kwargs)
        self.writer.write(message)

    async def receive(self):
        data = await self.reader.read(10000)
        return self.connection.unmarshall(data)

    def close(self):
        self.writer.close()
        self.reader = None
        self.writer = None
