"""
parameter message type.
"""
import dataclasses as dc
import typing as tp

from . import fa
from .. import ba, msg
from ..msg import td


@dc.dataclass
class ContractNewMod(ba.Mod):

    def get_margin(self, value: float) -> float:
        raise NotImplementedError

    def get_value(self, value: float) -> float:
        raise NotImplementedError

    def get_order_num(self, value: float, price: float) -> float:
        raise NotImplementedError

    pass


@dc.dataclass
class Contract(ContractNewMod):
    num_per_unit: float
    value_per_dot: float
    margin_ratio: float

    def get_margin(self, value: float) -> float:
        return abs(self.get_value(value) * self.margin_ratio)

    def get_value(self, value: float):
        return value * self.value_per_dot

    def get_order_num(self, value: float, price: float) -> float:
        return (value / self.margin_ratio / self.value_per_dot / price // self.num_per_unit) * self.num_per_unit


@dc.dataclass
class ContractNewMsg(fa.S):
    """
    be decided by the exchange.
    """
    cm: ContractNewMod


class ContractDelMsg(fa.S):
    pass


@dc.dataclass
class Cash(ba.Msg):
    """
    be decided by broker.
    """
    num: float
    pass


@dc.dataclass
class CommissionMod(ba.Mod):
    def get(self, c: ContractNewMod, ts: tp.Deque[td.Trade]):
        raise NotImplementedError

    pass


@dc.dataclass
class CommissionFuture(CommissionMod):
    rate: float

    def get(self, c: ContractNewMsg, ts: tp.Deque[td.Trade]) -> float:
        return sum((t.num for t in ts)) * self.rate

    pass


@dc.dataclass
class CommissionStockA(CommissionMod):
    tax: float
    commission: float
    min_commission: float

    def get(self, c: ContractNewMod, ts: tp.Deque[td.Trade]) -> float:
        return sum([(c.get_value(abs(t.num) * t.price * self.tax) if t.num < 0 else 0) +
                    max(self.min_commission, c.get_value(abs(t.num) * t.price) * self.commission)
                    for t in ts])

    pass


@dc.dataclass
class CommissionMsg(fa.S):
    """
    be decided by broker.
    """
    cm: CommissionMod
    pass


@dc.dataclass
class SlippageMod(ba.Mod):
    """
    be decided by exchange.
    """

    def get(self, c: ContractNewMod, o: td.OrderData, price):
        raise NotImplementedError


@dc.dataclass
class SlippageFix(SlippageMod):
    step: float

    def get(self, c: ContractNewMod, o: td.OrderData, price) -> float:
        return price + (self.step if o.num > 0 else -self.step)

    pass


@dc.dataclass
class SlippagePer(SlippageMod):
    rate: float

    def get(self, c: ContractNewMod, o: td.OrderData, price) -> float:
        return price * (1 + self.rate * (1 if o.num > 0 else -1))

    pass


@dc.dataclass
class SlippageMsg(fa.S):
    sm: SlippageMod
