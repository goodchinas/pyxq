import dataclasses as dc

import numpy as np

from .. import base
from .. import const


@dc.dataclass
class Base(base.Msg):
    pass


@dc.dataclass
class Settle(Base):
    pass


@dc.dataclass
class Settled(Base):
    cash: float
    equity: float
    commission: float


@dc.dataclass
class OrderData(base.Mod):
    symbol: str
    oc: const.OC
    price: float
    num: float

    @property
    def bs(self) -> float:
        return np.sign(self.num)


@dc.dataclass
class Limit(OrderData):
    pass


@dc.dataclass
class Market(OrderData):
    """
    不用 市价类型基本上由限价模拟：https://blog.csdn.net/u012724887/article/details/98502040
    """
    pass


@dc.dataclass
class OrderMsg(Base):
    od: OrderData
    pass


@dc.dataclass
class OrderRsp(Base):
    oms: OrderMsg


@dc.dataclass
class Ordered(OrderRsp):
    pass


@dc.dataclass
class Cancel(Base):
    order: OrderMsg
    pass


@dc.dataclass
class Trade(OrderRsp):
    price: float
    num: float

    @property
    def bs(self) -> float:
        return np.sign(self.num)

    pass


@dc.dataclass
class Rejected(OrderRsp):
    num: float


@dc.dataclass
class Canceled(OrderRsp):
    num: float
