class Context(object):

    def __init__(self, protocol):
        self.__protocols = protocol

    def handle(self, protocol_name: str, method_name: str, **kwargs):
        return getattr(self.__protocols[protocol_name], method_name)(**kwargs)
