from Crypto import Random
from Crypto.PublicKey import RSA


class ObliviousTransfer(object):

    def __init__(self, secrets, random_oracle):
        self.random = random_oracle
        self.m = secrets
        self.x = None
        self.key = None

    def get_public_key(self):
        random_generator = Random.new().read
        self.key = RSA.generate(1024, random_generator)
        public_key = self.key.publickey()
        return {'n': public_key.n, 'e': public_key.e}

    def get_random_integers(self):
        self.x = [self.random(m) for m in self.m]
        return {'x': self.x}

    def get_integers(self, v):
        k = [self.key.decrypt(v - x) for x in self.x]
        _m = [m_ + k_ for m_, k_ in zip(self.m, k)]
        return {'m': _m}
