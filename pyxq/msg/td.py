import dataclasses as dc

import numpy as np
from datetime import datetime
from .. import ba
from .. import cn


@dc.dataclass
class Base(ba.Msg):
    pass


@dc.dataclass
class SettleMsg(Base):
    pass


@dc.dataclass
class SettleData(ba.Mod):
    cash: float
    equity: float
    commission: float
    dt: datetime


@dc.dataclass
class OrderData(ba.Mod):
    symbol: str
    oc: cn.OC
    price: float
    num: float


@dc.dataclass
class Limit(OrderData):
    pass


@dc.dataclass
class Market(OrderData):
    """
    市价类型基本上由限价模拟：https://blog.csdn.net/u012724887/article/details/98502040
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
    def ls(self) -> cn.LS:
        return cn.LS.L if (self.num > 0 and self.oms.od.oc == cn.OC.O) or \
                          (self.num < 0 and self.oms.od.oc == cn.OC.C) \
            else cn.LS.S

    pass


@dc.dataclass
class Rejected(OrderRsp):
    num: float


@dc.dataclass
class Canceled(OrderRsp):
    num: float
