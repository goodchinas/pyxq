import dataclasses as dc
import typing as tp

from .. import ba
from ..msg import td


@dc.dataclass
class ContractMod(ba.Mod):
    num_per_unit: float
    value_per_dot: float
    margin_ratio: float

    def get_margin(self, value: float) -> float:
        return abs(self.get_value(value) * self.margin_ratio)

    def get_value(self, value: float):
        return value * self.value_per_dot

    pass


@dc.dataclass
class Symbol(ba.Msg):
    symbol: str


@dc.dataclass
class ContractMsg(Symbol):
    """
    be decided by the exchange.
    """
    cm: ContractMod


@dc.dataclass
class Cash(ba.Msg):
    """
    be decided by broker.
    """
    num: float
    pass


@dc.dataclass
class CommissionMod(ba.Mod):
    def get(self, c: ContractMod, ts: tp.Deque[td.Trade]):
        raise NotImplementedError

    pass


@dc.dataclass
class CommissionFuture(CommissionMod):
    rate: float

    def get(self, c: ContractMsg, ts: tp.Deque[td.Trade]) -> float:
        return sum((t.num for t in ts)) * self.rate

    pass


@dc.dataclass
class CommissionStockA(CommissionMod):
    tax: float
    commission: float
    min_commission: float

    def get(self, c: ContractMod, ts: tp.Deque[td.Trade]) -> float:
        return sum([(abs(t.num) * t.price * c.value_per_dot * self.tax if t.num < 0 else 0) +
                    max(self.min_commission, abs(t.num) * t.price * c.value_per_dot * self.commission)
                    for t in ts])

    pass


@dc.dataclass
class CommissionMsg(Symbol):
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
    symbol: str

    def get(self, c: ContractMod, o: td.OrderData, price):
        raise NotImplementedError


@dc.dataclass
class SlippageFix(SlippageMod):
    step: float

    def get(self, c: ContractMod, o: td.OrderData, price) -> float:
        return price + (self.step if o.num > 0 else -self.step)

    pass


@dc.dataclass
class SlippagePer(SlippageMod):
    rate: float

    def get(self, c: ContractMod, o: td.OrderData, price) -> float:
        return price * (1 + self.rate * (1 if o.num > 0 else -1))

    pass


@dc.dataclass
class SlippageMsg(Symbol):
    sm: SlippageMod
