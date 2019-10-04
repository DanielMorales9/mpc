import asyncio

from mpc.client.protocol import ObliviousTransfer


async def main(host, port):
    x = input("Do you want 1° or 2° integer?")
    if x == "1":
        b = 0
    else:
        b = 1

    protocol = ObliviousTransfer(host, port)
    mb = await protocol.run(b)
    print(f"Your choice is {mb}")


asyncio.run(main('localhost', 8080))
