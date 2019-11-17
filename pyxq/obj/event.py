from dataclasses import dataclass
from datetime import datetime
from .. import const as c
import uuid


@dataclass
class Event(object):
    """
    所有事件数据对象的父类
    """

    def __post_init__(self):
        self._key = self.cls_key()
        self.id = str(uuid.uuid1())

    @classmethod
    def cls_key(cls) -> int:
        return hash(cls)

    @property
    def key(self) -> int:
        return self._key


@dataclass
class Order(Event):
    symbol: str
    bs: c.BS
    oc: c.OC
    price: float
    volume: float

    pass


@dataclass
class Cancel(Event):
    symbol: str
    pass


@dataclass
class Trade(Event):
    order_id: str
    symbol: str
    bs: c.BS
    oc: c.OC
    price: float
    volume: float

    pass


@dataclass
class Tick(Event):
    symbol: str
    pass


@dataclass
class OrderBook(Event):
    symbol: str
    pass


@dataclass
class Kline(Event):
    symbol: str
    dt: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    pass
