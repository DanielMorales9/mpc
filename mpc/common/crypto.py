import hashlib
import operator
import random
import secrets

import sympy

# order of magnitude of prime in base 2
PRIME_BITS = 64


def next_prime(num):
    # next prime after num (skip 2)
    return 3 if num < 3 else sympy.nextprime(num)


def gen_prime(num_bits):
    # random 'bits-sized' prime
    r = secrets.randbits(num_bits)
    return next_prime(r)


def xor_bytes(seq1, seq2):
    return bytes(map(operator.xor, seq1, seq2))


def ot_hash(pub_key, msg_length):  # hash function for OT keys
    # use shake256 to ensure hash length equals msg length
    key_length = (pub_key.bit_length() + 7) // 8  # key length in bytes
    bytes = pub_key.to_bytes(key_length, byteorder="big")
    return hashlib.shake_256(bytes).digest(msg_length)


class PrimeGroup(object):
    # CryptographicOracle

    def __init__(self, prime=None):
        # PRIME_BITS is the number of bits or k
        self.prime = prime or gen_prime(num_bits=PRIME_BITS)
        self.primeM1 = self.prime - 1
        self.primeM2 = self.prime - 2
        self.generator = self.find_generator()

    def mul(self, num1, num2):  # multiplication
        return (num1 * num2) % self.prime

    def pow(self, base, exponent):  # exponentiation
        return pow(base, exponent, self.prime)

    def gen_pow(self, exponent):  # generator exponentiation
        return pow(self.generator, exponent, self.prime)

    def inv(self, num):  # multiplicative inverse
        return pow(num, self.primeM2, self.prime)

    def rand_int(self):  # random int in [1, prime-1]
        return random.randint(1, self.primeM1)

    def find_generator(self):
        # find random generator for group
        factors = sympy.primefactors(self.primeM1)
        while True:  # there are numerous generators
            candidate = self.rand_int()
            # so we'll find in a few tries
            for factor in factors:
                if 1 == self.pow(candidate, self.primeM1 // factor): break
            else:
                return candidate
