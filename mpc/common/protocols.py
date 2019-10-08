import random
import sys


class RandomOracle(object):

    def __init__(self, k=sys.maxsize):
        self.history = {}
        self.k = k

    def __call__(self, x):
        if x not in self.history:
            self.history[x] = random.randint(0, self.k)
        return self.history[x]
