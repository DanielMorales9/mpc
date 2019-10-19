import codecs
import json
import pickle

from mpc.common.crypto import xor_bytes, ot_hash
from mpc.common.protocols import GarbledCircuit


class ObliviousTransfer(object):

    def __init__(self, client, random_oracle):
        self.client = client
        self.random = random_oracle

    def get_public_key(self):
        self.client.send(self.__class__.__name__, self.get_public_key.__name__)
        key = self.client.receive()
        return key['n'], key['e']

    def get_random_integers(self):
        self.client.send(self.__class__.__name__, self.get_random_integers.__name__)
        res = self.client.receive()
        return res['x']

    def get_integers(self, v):
        self.client.send(self.__class__.__name__, self.get_integers.__name__, v=v)
        res = self.client.receive()
        return res['m']

    def run(self, b):
        n, e = self.get_public_key()
        rand_ints = self.get_random_integers()
        xb = rand_ints[b]
        k = self.random(xb)
        v = (xb + k ** e) % n
        ms = self.get_integers(v)
        m_b = ms[b] - k
        return m_b


class YaoObliviousTransfer(object):

    def __init__(self, client):
        self.client = client

    def get_keys(self):
        self.client.send(self.__class__.__name__, self.get_keys.__name__)
        res = self.client.receive()
        g = pickle.loads(codecs.decode(res['g'].encode(), "base64"))
        return g, res['c']

    def get_messages(self, h):
        self.client.send(self.__class__.__name__, self.get_messages.__name__, h=h)
        res = self.client.receive()
        e0 = codecs.decode(res['e0'].encode(), 'base64')
        e1 = codecs.decode(res['e1'].encode(), 'base64')
        return res['c1'], e0, e1

    def run(self, b):
        g, c = self.get_keys()
        x = g.rand_int()
        h_b = g.gen_pow(x)
        h_not_b = g.mul(c, g.inv(h_b))
        if b:
            c1, e0, e1 = self.get_messages(h_not_b)
            mb = xor_bytes(e1, ot_hash(g.pow(c1, x), len(e1)))
        else:
            c1, e0, e1 = self.get_messages(h_b)
            mb = xor_bytes(e0, ot_hash(g.pow(c1, x), len(e0)))
        return mb


def is_closed(data):
    if 'method' in data:
        return data['method'] == 'close'
    else:
        return False


class YaoGarbledCircuit(object):

    def __init__(self, client, oblivious_transfer):
        self.oblivious_transfer = oblivious_transfer
        self.client = client
        self.b_keys = None
        self.switch = {'YaoGarbledCircuit': self, 'YaoObliviousTransfer': self.oblivious_transfer}

    def circuit_input(self, circuit, table, output_p_bits, active_labels):
        # Creates garbled circuit
        self.client.connect()
        # json does not serialize tuple as key and bytes as any value
        table = {k: [{'k': ki, 'h': vi.decode('utf-8')} for ki, vi in v.items()] for k, v in table.items()}
        active_labels = {k: (v1.decode('utf-8'), v2) for k, (v1, v2) in active_labels.items()}
        kwargs = dict(circuit=circuit, table=table, output_p_bits=output_p_bits, active_labels=active_labels)
        self.client.send(self.__class__.__name__, self.circuit_input.__name__, **kwargs)

    def ot(self, w):
        secret = [pickle.dumps(k) for k in self.b_keys[w]]
        self.oblivious_transfer.set_secrets(secret)

    def run(self, circuit_spec, inputs):
        circuit = GarbledCircuit(circuit_spec)
        a_wires = circuit_spec['alice']
        b_wires = circuit_spec['bob']
        active_labels = circuit.encode_labels(inputs, a_wires)
        self.circuit_input(circuit_spec, circuit.garbled_tables, circuit.out_p_bits, active_labels)
        self.b_keys = circuit.keys_of_wires(b_wires)

        # share keys by using ot
        data = self.client.receive()
        while not is_closed(data):
            res = getattr(self.switch[data['app']], data['method'])(**data['kwargs'])
            if res:
                self.client.socket.send(json.dumps(res).encode('utf-8'))
            data = self.client.receive()

        data = self.client.receive()
        return {int(k): v for k, v in data.items()}
