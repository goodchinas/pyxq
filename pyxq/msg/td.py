import dataclasses as dc
import numpy as np

from .. import base
from .. import const


@dc.dataclass
class Info(base.Msg):
    pass


@dc.dataclass
class Settle(Info):
    pass


@dc.dataclass
class Settled(Info):
    cash: float
    equity: float
    commission: float


@dc.dataclass
class Order(Info):
    symbol: str
    oc: const.OC
    price: float
    order_num: float  # 委托
    trade_num: float = dc.field(init=False, default=0)  # 成交
    cancel_nm: float = dc.field(init=False, default=0)  # 取消
    reject_nm: float = dc.field(init=False, default=0)  # 拒绝

    @property
    def bs(self) -> float:
        return np.sign(self.order_num)


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
class OrderRsp(Info):
    order: Order


@dc.dataclass
class Ordered(OrderRsp):
    pass


@dc.dataclass
class Cancel(Info):
    order: Order
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
