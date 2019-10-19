import json

from mpc.client.client import SocketClient
from mpc.client.protocols import YaoGarbledCircuit, ObliviousTransfer
from mpc.common.protocols import RandomOracle
from mpc.server._protocols import YaoObliviousTransfer


# def main(host, port):
#     # oblivious transfer
#     x = input("Input b: ")
#     b = int(x)
#
#     client = SocketClient(host=host, port=port)
#     random = RandomOracle()
#     with client:
#         protocol = ObliviousTransfer(client, random)
#         mb = protocol.run(b)
#         print(f"Your choice is {mb}")


def main(host, port):
    input = [1]
    client = SocketClient(host=host, port=port)
    random = RandomOracle()
    ot = YaoObliviousTransfer(random)
    protocol = YaoGarbledCircuit(client, ot)
    circuit_spec = json.load(open('yao.json'))
    with client:
        output = protocol.run(circuit_spec, input)
        for gate in circuit_spec['out']:
            print("Out Gate: %s\tResult: %s" % (gate, output[gate]))


main('localhost', 8080)
