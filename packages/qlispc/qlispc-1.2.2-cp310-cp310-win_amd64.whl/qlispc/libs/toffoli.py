import numpy as np


def ccz(c1, c2, t):
    return [
        ('Cnot', c2, t),
        ('-T', t),
        ('Cnot', c1, t),
        ('T', t),
        ('Cnot', c2, t),
        ('-T', t),
        ('Cnot', c1, t),
        ('T', c2),
        ('T', t),
        ('Cnot', c1, c2),
        ('T', c1),
        ('-T', c2),
        ('Cnot', c1, c2),
    ]


def ccx(c1, c2, t):
    return [
        ('H', t),
        *ccz(c1, c2, t),
        ('H', t),
    ]


def rccx(c1, c2, t):
    """
    Relative-phase Toffoli gates

    1  0  0  0  0  0  0  0
    0  1  0  0  0  0  0  0
    0  0  1  0  0  0  0  0
    0  0  0  1  0  0  0  0
    0  0  0  0  1  0  0  0
    0  0  0  0  0 -1  0  0
    0  0  0  0  0  0  0  1
    0  0  0  0  0  0  1  0

    DOI: 10.1103/PhysRevA.93.022311
    https://arxiv.org/pdf/quant-ph/0312225
    """
    return [
        (('Ry', np.pi / 4), t),
        ('Cnot', c2, t),
        (('Ry', np.pi / 4), t),
        ('Cnot', c1, t),
        (('Ry', -np.pi / 4), t),
        ('Cnot', c2, t),
        (('Ry', -np.pi / 4), t),
    ]
