import collections
import importlib
import json

from mpc.common.protocols import RandomOracle
from mpc.server._protocols import ObliviousTransfer

PROTOCOL_DEFAULTS = {
    'RandomOracle': {},
    'ObliviousTransfer': {
        'random_oracle': '@RandomOracle'
    }
}


def merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def substitute(this, other):
    return {k: other[v[1:]] if str(v).startswith('@') else v for k, v in this.items()}


class ProtocolFactory(object):

    @classmethod
    def create(cls):
        file_properties = json.load(open('properties.json'))
        properties = PROTOCOL_DEFAULTS.copy()
        merge(properties, file_properties)

        protocols = {}

        for k, v in properties.items():
            v = substitute(v, protocols)
            module = importlib.import_module(cls.__module__)
            factory = getattr(module, f'{k}Factory')
            protocols[k] = factory.create(**v)

        return protocols


class ObliviousTransferFactory:

    @staticmethod
    def create(**kwargs):
        return ObliviousTransfer(**kwargs)


class RandomOracleFactory:

    @staticmethod
    def create(**kwargs):
        return RandomOracle(**kwargs)
