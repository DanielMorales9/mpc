import asyncio
import socket

from mpc.common.connection import marshall_request, unmarshall_response


# class AsyncClient(object):
#
#     def __init__(self, host=None, port=None):
#         self.loop = asyncio.get_event_loop()
#         self.host = host
#         self.port = port
#         self.reader = None
#         self.writer = None
#
#     async def connect(self):
#         if self.writer:
#             self.writer.close()
#         self.reader, self.writer = await asyncio.open_connection(self.host, self.port, loop=self.loop)
#
#     async def send(self, *args, **kwargs):
#         await self.connect()
#         message = marshall_request(*args, **kwargs)
#         self.writer.write(message)
#
#     async def receive(self):
#         data = await self.reader.read(10000)
#         return unmarshall_response(data)
#
#     def close(self):
#         self.writer.close()


class SocketClient(object):

    def __init__(self, socket=None, host=None, port=None):
        assert not all((socket, host, port))
        self.socket = socket
        self.host = host
        self.port = port

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

    def send(self, *args, **kwargs):
        message = marshall_request(*args, **kwargs)
        self.socket.send(message)

    def receive(self):
        data = self.socket.recv(10000)
        return unmarshall_response(data)

    def close(self):
        self.socket.close()
