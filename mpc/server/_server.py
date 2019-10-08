import asyncio

from mpc.server._context import Context
from mpc.server._factories import ProtocolFactory
from mpc.server._transport import Transport


class Server(object):

    def __init__(self):
        protocol = ProtocolFactory.create()
        self.context = Context(protocol)

    def run(self, host='127.0.0.1', port=8080):
        context = self.context

        async def main():
            loop = asyncio.get_running_loop()
            server = await loop.create_server(lambda: Transport(context), host, port)
            await server.serve_forever()

        asyncio.run(main())
