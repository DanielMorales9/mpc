import socket

from mpc.common.connection import marshall_response, unmarshall_request
from mpc.server._context import Context
from mpc.server._factories import ProtocolFactory


class SocketTransport(object):

    def __init__(self, host, port):
        self.context = None
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen(1)
        self.socket = None

    def connect(self):
        self.socket, client = self.s.accept()
        # TODO should be initialized and injected differently,
        #  maybe it has a lifecycle manager that copies objects clears
        #  and override attributes
        self.context = Context(self.socket)

    def receive(self):
        data = self.socket.recv(10000)
        if not data:
            raise ConnectionAbortedError
        protocol, method, data = unmarshall_request(data)
        response = self.context.handle(protocol, method, **data)
        data = marshall_response(**response)
        self.socket.send(data)

    def close(self):
        self.socket.close()
