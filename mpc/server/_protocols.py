import codecs
import pickle
import random

from Crypto import Random
from Crypto.PublicKey import RSA

from mpc.common.crypto import PrimeGroup, ot_hash, xor_bytes
from mpc.common.protocols import GarbledCircuit


def generate_rsa():
    # TODO wrap into class and use DI to inject into OT
    # TODO switch to cryptography instead of pycrypto
    random_generator = Random.new().read
    return RSA.generate(1024, random_generator)


class ObliviousTransfer(object):

    def __init__(self, secrets=None, random_oracle=None):
        self.random = random_oracle
        self.m = secrets
        self.x = None
        self.key = None

    def get_public_key(self):
        self.key = generate_rsa()
        public_key = self.key.publickey()
        return {'n': public_key.n, 'e': public_key.e}

    def get_random_integers(self):
        self.x = [self.random(m) for m in self.m]
        return {'x': self.x}

    def get_integers(self, v):
        k = [self.key.decrypt(v - x) for x in self.x]
        _m = [m_ + k_ for m_, k_ in zip(self.m, k)]
        return {'m': _m}

    def set_secrets(self, secrets):
        self.m = secrets


class YaoObliviousTransfer(object):

    def __init__(self, secrets=None):
        self.m = secrets
        self.g = PrimeGroup()
        self.c = None

    def get_keys(self):
        self.c = self.g.gen_pow(self.g.rand_int())
        g = codecs.encode(pickle.dumps(self.g), "base64").decode()
        return {'g': g, 'c': self.c}

    def get_messages(self, h):
        h1 = self.g.mul(self.c, self.g.inv(h))
        k = self.g.rand_int()
        c1 = self.g.gen_pow(k)
        e0 = xor_bytes(self.m[0], ot_hash(self.g.pow(h, k), len(self.m[0])))
        e1 = xor_bytes(self.m[1], ot_hash(self.g.pow(h1, k), len(self.m[1])))
        e0 = codecs.encode(e0, 'base64').decode()
        e1 = codecs.encode(e1, 'base64').decode()
        return {'c1': c1, 'e0': e0, 'e1': e1}

    def set_secrets(self, secrets):
        self.m = secrets


class YaoGarbledCircuit(object):

    def __init__(self, inputs, client, oblivious_transfer_client):
        self.client = client
        self.inputs = inputs
        self.oblivious_transfer = oblivious_transfer_client

    def circuit_input(self, circuit, table, output_p_bits, active_labels):
        circuit = circuit
        table = {int(k): {tuple(vi['k']): vi['h'].encode('utf-8') for vi in v} for k, v in table.items()}
        active_labels = {int(k): (v1.encode('utf-8'), v2) for k, (v1, v2) in active_labels.items()}
        output_p_bits = {int(k): v for k, v in output_p_bits.items()}
        a_keys = active_labels

        wires = circuit['bob']
        clear_input = {w: i for w, i in zip(wires, self.inputs)}
        b_keys = {}
        for w, i in clear_input.items():
            self.client.send('YaoGarbledCircuit', 'ot', w=w)
            mb = self.oblivious_transfer.run(i)
            b_keys[w] = pickle.loads(mb)
        self.client.send('YaoGarbledCircuit', 'close')
        result = GarbledCircuit.evaluate(circuit, table, output_p_bits, a_keys, b_keys)
        return {str(k): v for k, v in result.items()}
