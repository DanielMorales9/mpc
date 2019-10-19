import pickle
import random
import sys

from cryptography.fernet import Fernet


class RandomOracle(object):

    def __init__(self, k=sys.maxsize):
        self.history = {}
        self.k = k

    def __call__(self, x):
        if x not in self.history:
            self.history[x] = random.randint(0, self.k)
        return self.history[x]


def encrypt(key, data: bytes):
    """
    Encrypt a message.
        Parameters:
            key: the encryption key
            data: the message to encrypt
        Returns:
            encrypt_msg: a byte stream, the encrypted message
    """
    f = Fernet(key)
    return f.encrypt(data)


def decrypt(key, data):
    """
    Decrypt a message.
        Parameters:
            key: the decryption key
            data: the message to decrypt
        Returns
            decrypt_msg: a byte stream, the decrypted message
    """
    f = Fernet(key)
    return f.decrypt(data)


def is_unary_op(gate_in, wire_inputs):
    return (len(gate_in) < 2) and (gate_in[0] in wire_inputs)


def is_binary_operator(gate_in, wire_inputs):
    return (gate_in[0] in wire_inputs) and (gate_in[1] in wire_inputs)


class GarbledCircuit:
    """
    A representation of a garbled circuit.

    Parameters:
        circuit: dict
            containing circuit specification
            example circuit:
                {
                    "circuit": {
                        "name"  : "Example circuit",
                        "alice" : [1, 2],
                        "bob"   : [3, 4],
                        "out"   : [7],
                        "gates" : [
                            {"id" : 5, "type" : "AND", "in" : [1, 3]},
                            {"id" : 6, "type" : "XOR", "in" : [2, 4]},
                            {"id" : 7, "type" : "OR",  "in" : [5, 6]}
                        ]
                    }
                }
        p_bits: dict
            p-bits for the given circuit
    """

    def __init__(self, circuit, p_bits=None):
        if p_bits is None:
            p_bits = {}
        self.name = circuit['name']
        self.output = circuit['out']
        self.gates = circuit["gates"]  # list of gates
        self.wires = None  # list of circuit wires

        self.p_bits = {}  # dict of p-bits
        self.keys = {}  # dict of keys
        self.garbled_tables = {}  # dict of garbled table

        self._init_wires()
        self._init_p_bits(p_bits)
        self._init_keys()
        self._init_garbled_tables()
        self.out_p_bits = {wire: self.p_bits[wire] for wire in self.output}

    def _init_wires(self):
        """
            Retrieve all wire IDs from the circuit.
        """
        wires = set()
        for gate in self.gates:
            wires.add(gate["id"])
            wires.update(set(gate["in"]))
        self.wires = list(wires)

    def _init_p_bits(self, p_bits):
        """
            Creates a dict mapping each wire to a random p-bit.
        """
        self.p_bits = p_bits or {wire: random.randint(0, 1) for wire in self.wires}

    def _init_keys(self):
        """
            Creates pair of keys for each wire.
        """

        self.keys = {wire: (Fernet.generate_key(), Fernet.generate_key()) for wire in self.wires}

    def _init_garbled_tables(self):
        """
            Creates the garbled table of each gate.
        """
        for gate in self.gates:
            g_gate = GarbledGate(gate, self.keys, self.p_bits)
            self.garbled_tables[gate["id"]] = g_gate.get_garbled_table()

    def print_garbled_tables(self):
        """
            Prints p-bits and a clear representation of all garbled table.
        """
        print("NAME: {0}".format(self.name))

        print("P-BITS:".format(self.p_bits))
        for wire, p_bit in self.p_bits.items():
            print("* {0}: {1}".format(wire, p_bit))
        print()

        for gate in self.gates:
            garbled_table = GarbledGate(gate, self.keys, self.p_bits)
            garbled_table.print_garbled_table()
            print()

    @staticmethod
    def evaluate(circuit, g_tables, p_bits_out, a_inputs, b_inputs):
        """
        Evaluate yao circuit with given secrets.
            Parameters:
                circuit: dict
                    containing circuit spec
                g_tables: dict
                    garbled table of yao circuit
                p_bits_out: dict
                    p-bits of outputs
                a_inputs: dict
                    mapping Alice's wires to (key, encr_bit) secrets
                b_inputs: dict
                    mapping Bob's wires to (key, encr_bit) secrets
            Returns:
                evaluation: dict
                    mapping output wires with the result bit
        """
        gates = circuit['gates']  # dict containing circuit gates
        wire_outputs = circuit['out']  # list of output wires
        wire_inputs = {}  # dict containing Alice and Bob secrets
        evaluation = {}  # dict containing result of evaluation

        wire_inputs.update(a_inputs)
        wire_inputs.update(b_inputs)
        # Iterate over all gates
        for gate in sorted(gates, key=lambda g: g["id"]):
            gate_id, gate_in, msg = gate["id"], gate["in"], None

            # Special case if it's a NOT gate
            if is_unary_op(gate_in, wire_inputs):
                # Fetch input key associated with the gate's input wire
                key_in, bit_in = wire_inputs[gate_in[0]]
                # Fetch the encrypted message in the gate's garbled table
                encrypted_msg = g_tables[gate_id][(bit_in,)]
                # Decrypt message
                msg = decrypt(key_in, encrypted_msg)

            # Else the gate has two input wires (same model)
            elif is_binary_operator(gate_in, wire_inputs):
                key_a, bit_a = wire_inputs[gate_in[0]]
                key_b, bit_b = wire_inputs[gate_in[1]]
                encrypted_msg = g_tables[gate_id][(bit_a, bit_b)]
                msg = decrypt(key_b, decrypt(key_a, encrypted_msg))

            if msg:
                wire_inputs[gate_id] = pickle.loads(msg)

        # After all gates have been evaluated, we populate the dict of results
        for out in wire_outputs:
            evaluation[out] = wire_inputs[out][1] ^ p_bits_out[out]

        return evaluation

    def encode_labels(self, inputs, wires):
        return {wire: (self.keys[wire][inp], self.p_bits[wire] ^ inp) for inp, wire in zip(inputs, wires)}

    def keys_of_wires(self, b_wires):
        return {w: ((self.keys[w][0], 0 ^ self.p_bits[w]), (self.keys[w][1], 1 ^ self.p_bits[w])) for w in b_wires}


class GarbledGate:
    """
        A represent action of a garbled gate.
        Parameters:
            gate: dict
                containing gate spec
            keys: dict
                mapping each wire to a pair of keys
            p_bits: dict
                mapping each wire to its p-bit
    """

    def __init__(self, gate, keys, p_bits):
        self.keys = keys  # dict of yao circuit keys
        self.p_bits = p_bits  # dict of p-bits
        self.input = gate["in"]  # list of secrets'ID
        self.output = gate["id"]  # ID of output
        self.gate_type = gate["type"]  # Gate type: OR, AND, ...
        self.garbled_table = {}  # The garbled table of the gate
        # A clear representation of the garbled table for debugging purposes
        self.clear_garbled_table = {}

        # Create the garbled table according to the gate type
        switch = {
            "OR": lambda b1, b2: b1 or b2,
            "AND": lambda b1, b2: b1 and b2,
            "XOR": lambda b1, b2: b1 ^ b2,
            "NOR": lambda b1, b2: not (b1 or b2),
            "NAND": lambda b1, b2: not (b1 and b2),
            "XNOR": lambda b1, b2: not (b1 ^ b2)
        }

        # NOT gate is a special case since it has only one input
        if self.gate_type == "NOT":
            self._generate_garbled_table_not()
        else:
            operator = switch[self.gate_type]
            self._generate_garbled_table(operator)

    def _generate_garbled_table_not(self):
        """
            Creates the garbled table of a NOT gate,
            by enumerating all the possible combination of secrets
        """
        inp, out = self.input[0], self.output

        # For each entry in the garbled table
        for input_bit in (0, 1):
            # Retrieve original bit
            bit_in = input_bit ^ self.p_bits[inp]
            # Compute output bit according to the gate type
            bit_out = int(not bit_in)
            # Compute encrypted bit with the p-bit table
            output_bit = bit_out ^ self.p_bits[out]
            # Retrieve related keys
            key_in = self.keys[inp][bit_in]
            key_out = self.keys[out][bit_out]

            # Serialize the output key along with the encrypted bit
            msg = pickle.dumps((key_out, output_bit))
            # Encrypt message and add it to the garbled table
            self.garbled_table[(input_bit,)] = encrypt(key_in, msg)
            # Add to the clear table indexes of each keys
            self.clear_garbled_table[(input_bit,)] = [(inp, bit_in), (out, bit_out), output_bit]

    def _generate_garbled_table(self, operator):
        """
            Creates the garbled table of a 2-input gate.
            Parameters:
                operator: the logical function corresponding to the 2-input gate type
        """
        in_a, in_b, out = self.input[0], self.input[1], self.output

        # Same model as for the NOT gate except for 2 secrets instead of 1
        for input_bit_a in (0, 1):
            for input_bit_b in (0, 1):
                bit_a = input_bit_a ^ self.p_bits[in_a]
                bit_b = input_bit_b ^ self.p_bits[in_b]
                bit_out = int(operator(bit_a, bit_b))
                output_bit = bit_out ^ self.p_bits[out]
                key_a = self.keys[in_a][bit_a]
                key_b = self.keys[in_b][bit_b]
                key_out = self.keys[out][bit_out]

                msg = pickle.dumps((key_out, output_bit))
                self.garbled_table[(input_bit_a, input_bit_b)] = encrypt(key_a, encrypt(key_b, msg))
                self.clear_garbled_table[(input_bit_a, input_bit_b)] =\
                    [(in_a, bit_a), (in_b, bit_b), (out, bit_out), output_bit]

    def print_garbled_table(self):
        """
            Prints a clear representation of the garbled table.
        """
        print("GATE: {0}, TYPE: {1}".format(self.output, self.gate_type))
        for k, v in self.clear_garbled_table.items():
            # If it's a 2-input gate
            if len(k) > 1:
                key_a, key_b, key_out = v[0], v[1], v[2]
                output_bin = v[3]
                print("[{0}, {1}]: [{2}, {3}][{4}, {5}]([{6}, {7}], {8})" \
                      .format(k[0], k[1], key_a[0], key_a[1], key_b[0], key_b[1], key_out[0], key_out[1], output_bin))
            # Else it's a NOT gate
            else:
                key_in, key_out = v[0], v[1]
                output_bin = v[2]
                print("[{0}]: [{1}, {2}]([{3}, {4}], {5})" \
                      .format(k[0], key_in[0], key_in[1], key_out[0], key_out[1], output_bin))

    def get_garbled_table(self):
        """
            Returns the garbled table of the gate.
        """
        return self.garbled_table
