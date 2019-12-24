import enum

"""
constant data。
"""


class OC(enum.Enum):
    O = 1
    C = -1


class LS(enum.Enum):
    """
    the instrument be made of the information symbol and that long or short.
    """
    L = 1
    S = -1


class ACTOR(enum.Enum):
    """
    the actor enum value.
    """
    GATEWAY = 'gateway'
    BROKER = 'broker'
    EXCHANGE = 'exchange'


if __name__ == '__main__':
    pass
