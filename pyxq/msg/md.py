"""
market data type.
"""
import dataclasses as dc

from .. import base
from . import td


@dc.dataclass
class Info(base.Msg):
    """
    market data base class.
    """
    symbol: str


@dc.dataclass
class Tick(Info):
    price: float
    volume: float
    pass


@dc.dataclass
class Kline(Info):
    open: float
    high: float
    low: float
    close: float
    volume: float

    pass


@dc.dataclass
class OrderBook(Info):
    """
    某一时刻，委买委卖列表队列
    """
    pass
