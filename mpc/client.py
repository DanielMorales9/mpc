import asyncio

from mpc.client.protocols import ObliviousTransfer

from mpc.client.client import Client
from mpc.common.protocols import RandomOracle


async def main(host, port):
    x = input("Input b: ")
    b = int(x)

    client = Client(host, port)
    random = RandomOracle()
    protocol = ObliviousTransfer(client, random)
    mb = await protocol.run(b)
    print(f"Your choice is {mb}")


asyncio.run(main('localhost', 8080))
