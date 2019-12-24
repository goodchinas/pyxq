import dataclasses as dc

from .. import ba, msg

"""
market data type.
"""


@dc.dataclass
class Tick(msg.Symbol):
    price: float
    volume: float
    pass


@dc.dataclass
class OrderBook(msg.Symbol):
    """
    某一时刻，委买委卖列表队列
    """
    pass


@dc.dataclass
class Open(ba.Msg):
    pass


class Close(ba.Msg):
    pass
