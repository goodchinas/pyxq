import dataclasses as dc
from datetime import datetime

import numpy as np

import pyxq.base
from pyxq import const


@dc.dataclass
class Trade(pyxq.base.Msg):
    order_id: str
    symbol: str
    oc: const.OC
    price: float
    volume: float
    dt: datetime

    @property
    def bs(self) -> float:
        return np.sign(self.volume)

    pass


@dc.dataclass
class Ordered(pyxq.base.Msg):
    order_id: str
    broker: str = None
    exchange: str = None


@dc.dataclass
class Rejected(pyxq.base.Msg):
    order_id: str
    num: float


@dc.dataclass
class Canceled(pyxq.base.Msg):
    order_id: str
    num: float


# fixme 循环调用的问题，这里留下order msg，拆解功能roder到account，order作为orders的属性

@dc.dataclass
class Order(pyxq.base.Msg):
    symbol: str
    oc: const.OC
    price: float
    order_num: float  # 委托
    trade_num: float = dc.field(init=False, default=0)  # 成交
    cancel_nm: float = dc.field(init=False, default=0)  # 取消
    reject_nm: float = dc.field(init=False, default=0)  # 拒绝
    dt: datetime


@dc.dataclass
class Limit(Order):
    pass


@dc.dataclass
class Market(Order):
    """
    不用 市价类型基本上由限价模拟：https://blog.csdn.net/u012724887/article/details/98502040
    """
    pass


@dc.dataclass
class Cancel(pyxq.base.Msg):
    order_id: str

    pass
