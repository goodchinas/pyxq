import dataclasses as dc
from collections import defaultdict
import typing as tp
from .. import ba, msg

"""
market data type.
"""


@dc.dataclass
class Tick(msg.S):
    price: float
    volume: float
    pass


@dc.dataclass
class OrderBook(msg.S):
    pass


@dc.dataclass
class Open(ba.Msg):
    pass


class Close(ba.Msg):
    pass


@dc.dataclass
class Factor(msg.S):
    data: dict
    pass
