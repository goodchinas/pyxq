"""
market message type.
"""
import dataclasses as dc

from . import fa
from .. import ba


@dc.dataclass
class Tick(fa.S):
    price: float
    volume: float
    pass


@dc.dataclass
class OrderBook(fa.S):
    pass


@dc.dataclass
class Open(ba.Msg):
    pass


class Close(ba.Msg):
    pass


@dc.dataclass
class Factor(fa.S):
    data: dict
    pass
