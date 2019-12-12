import dataclasses as dc
from datetime import datetime

import pyxq.base


@dc.dataclass
class Tick(pyxq.base.Msg):
    symbol: str

    pass


@dc.dataclass
class Kline(pyxq.base.Msg):
    symbol: str
    dt: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    pass


@dc.dataclass
class OrderBook(pyxq.base.Msg):
    symbol: str

    pass
