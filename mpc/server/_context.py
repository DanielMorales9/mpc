from mpc.server._factories import ProtocolFactory


class Context(object):

    def __init__(self, socket):
        self.socket = socket
        self.__protocols = ProtocolFactory.create(socket=socket)

    def handle(self, protocol_name: str, method_name: str, **kwargs):
        return getattr(self.__protocols[protocol_name], method_name)(**kwargs)
