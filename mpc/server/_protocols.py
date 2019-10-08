import random
import sys
from abc import ABCMeta, abstractmethod

from Crypto import Random
from Crypto.PublicKey import RSA

MAX_RAND = 2 * 1024


class IProtocol(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_methods(self):
        pass


class ObliviousTransfer(IProtocol):

    def __init__(self, random_oracle):
        self.random = random_oracle
        self.methods = [self.get_public_key, self.get_random_integers, self.get_integers]
        self.key = None
        self.x0 = None
        self.x1 = None
        self.m0 = 2**0
        self.m1 = 2**10

    def init_messages(self, m0, m1):
        self.m0 = m0
        self.m1 = m1

    def get_methods(self):
        return self.methods

    def get_public_key(self):
        random_generator = Random.new().read
        self.key = RSA.generate(1024, random_generator)
        public_key = self.key.publickey()
        return {'n': public_key.n, 'e': public_key.e}

    def get_random_integers(self):
        self.x0 = self.random(self.m0)
        self.x1 = self.random(self.m1)
        return {'x0': self.x0, 'x1': self.x1}

    def get_integers(self, v):
        k0, k1 = self.get_ks(v)
        m_0 = self.m0 + k0
        m_1 = self.m1 + k1
        return {'m_0': m_0, 'm_1': m_1}

    def get_ks(self, v):
        k0 = self.key.decrypt(v - self.x0)
        k1 = self.key.decrypt(v - self.x1)
        return k0, k1
