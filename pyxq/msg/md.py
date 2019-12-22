"""
market data type.
"""
import dataclasses as dc

from .. import ba


@dc.dataclass
class Symbol(ba.Msg):
    """
    market data base class.
    """
    symbol: str


@dc.dataclass
class Tick(Symbol):
    price: float
    volume: float
    pass


@dc.dataclass
class _Kline(Symbol):
    open: float
    high: float
    low: float
    close: float
    volume: float
    pass


@dc.dataclass
class Open(ba.Msg):
    pass


class Close(ba.Msg):
    pass


@dc.dataclass
class OrderBook(Symbol):
    """
    某一时刻，委买委卖列表队列
    """
    pass
