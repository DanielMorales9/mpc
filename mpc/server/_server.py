from mpc.server._transport import SocketTransport


class Server(object):

    def __init__(self):
        self.transport = None

    def run(self, host='127.0.0.1', port=8080):
        self.transport = SocketTransport(host, port)

        while True:
            self.transport.connect()
            while True:
                try:
                    self.transport.receive()
                except ConnectionAbortedError:
                    self.transport.close()
                    break
