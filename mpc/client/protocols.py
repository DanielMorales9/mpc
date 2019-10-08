class ObliviousTransfer(object):

    def __init__(self, client, random_oracle):
        assert client is not None, "Client cannot be None"
        self.client = client
        self.random = random_oracle

    async def get_public_key(self):
        await self.client.connect()
        # TODO improve this
        self.client.send(self.__class__.__name__, self.get_public_key.__name__)
        res = await self.client.receive()
        key = res[-1]
        self.client.close()
        return key['n'], key['e']

    async def get_random_integers(self):
        await self.client.connect()
        self.client.send(self.__class__.__name__, self.get_random_integers.__name__)
        res = await self.client.receive()
        res = res[-1]
        self.client.close()
        return res['x']

    async def get_integers(self, v):
        await self.client.connect()
        self.client.send(self.__class__.__name__, self.get_integers.__name__, v=v)
        res = await self.client.receive()
        res = res[-1]
        self.client.close()
        return res['m']

    async def run(self, b):
        n, e = await self.get_public_key()
        rand_ints = await self.get_random_integers()
        xb = rand_ints[b]
        k = self.random(xb)
        v = (xb + k ** e) % n
        ms = await self.get_integers(v)
        m_b = ms[b] - k
        return m_b
