from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event(object):
    def __post_init__(self):
        self._key = self.cls_key()

    @classmethod
    def cls_key(cls) -> int:
        return hash(cls)

    @property
    def key(self) -> int:
        return self._key


@dataclass
class Order(Event):
    """
    fixme: OrderReq and OrderCancel is method,is not class.
    委托
    注：通过account指定账号
    """
    datetime: datetime
    pass


@dataclass
class Cancel(Event):
    pass


@dataclass
class Trade(Event):
    """
    成交
    """
    pass


@dataclass
class Tick(Event):
    pass


@dataclass
class Kline(Event):
    pass
