import collections
import importlib
import json

from mpc.client.client import SocketClient
from mpc.client.protocols import YaoObliviousTransfer
from mpc.common.protocols import RandomOracle
from mpc.server._protocols import ObliviousTransfer, YaoGarbledCircuit

PROTOCOL_DEFAULTS = {
    'RandomOracle': {},
    'ObliviousTransfer': {
        'random_oracle': '@RandomOracle'
    },
    'Client': {
        'socket': ':socket'
    },
    'YaoObliviousTransferClient': {
        'client': '@Client'
    },
    'YaoGarbledCircuit': {
        'oblivious_transfer_client': '@YaoObliviousTransferClient',
        'client': '@Client',
    }
}


def deep_merge(this, other):
    def rec(a, b):
        for k, v in b.items():
            if (k in a and isinstance(a[k], dict)
                    and isinstance(b[k], collections.Mapping)):
                rec(a[k], b[k])
            else:
                a[k] = b[k]

    this = this.copy()
    rec(this, other)
    return this


def override(this, other):
    return {k: other[k] if k in other else v for k, v in this.items()}


def substitute(this, other):
    return {k: other[v[1:]] if str(v).startswith('@') else v for k, v in this.items()}


class ProtocolFactory(object):

    @classmethod
    def create(cls, **kwargs):
        file_properties = json.load(open('properties.json'))
        properties = deep_merge(PROTOCOL_DEFAULTS, file_properties)

        protocols = {}

        for k, v in properties.items():
            v = substitute(v, protocols)
            module = importlib.import_module(cls.__module__)
            factory = getattr(module, f'{k}Factory')
            w = override(v, kwargs)
            protocols[k] = factory.create(**w)

        return protocols


class ObliviousTransferFactory:

    @staticmethod
    def create(**kwargs):
        return ObliviousTransfer(**kwargs)


class RandomOracleFactory:

    @staticmethod
    def create(**kwargs):
        return RandomOracle(**kwargs)


class ClientFactory:

    @staticmethod
    def create(**kwargs):
        return SocketClient(**kwargs)


class YaoGarbledCircuitFactory:

    @staticmethod
    def create(**kwargs):
        return YaoGarbledCircuit(**kwargs)


class YaoObliviousTransferClientFactory:

    @staticmethod
    def create(**kwargs):
        return YaoObliviousTransfer(**kwargs)
