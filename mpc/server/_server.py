import asyncio
from typing import Type

from mpc.server._events import EventHook
from mpc.server._protocol import ObliviousTransfer, IProtocol
from mpc.server._transport import Transport

SECURE_PROTOCOLS = [ObliviousTransfer]


class Server(object):

    def __init__(self):
        self.hook = EventHook()
        self.protocol = []
        self.register_protocols(*SECURE_PROTOCOLS)

    def register_protocols(self, *protocols):
        for protocol in protocols:
            p = protocol()
            self.hook.subscribe(p)
            self.protocol.append(p)

    def run(self, host='127.0.0.1', port=8080):
        hook = self.hook

        async def main():
            loop = asyncio.get_running_loop()
            server = await loop.create_server(lambda: Transport(hook), host, port)
            await server.serve_forever()

        asyncio.run(main())
