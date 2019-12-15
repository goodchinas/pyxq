import dataclasses as dc
import typing as tp
from .. import base, const
from ..msg import td


@dc.dataclass
class Contract(base.Msg):
    """
    be decided by the exchange.
    """
    symbol: str
    num_per_unit: float
    value_per_dot: float
    margin_ratio: float

    def get_margin(self, value: float) -> float:
        return abs(self.get_value(value) * self.margin_ratio)

    def get_value(self, value: float):
        return value * self.value_per_dot

    pass


@dc.dataclass
class Cash(base.Msg):
    """
    be decided by broker.
    """
    num: float
    pass


@dc.dataclass
class Commission(base.Msg):
    """
    be decided by broker.
    """
    symbol: str

    def get(self, c: Contract, ts: tp.Deque[td.Trade]):
        raise NotImplementedError

    pass


@dc.dataclass
class CommissionFuture(Commission):
    rate: float

    def get(self, c: Contract, ts: tp.Deque[td.Trade]) -> float:
        return sum((t.num for t in ts)) * self.rate

    pass


@dc.dataclass
class CommissionStockA(Commission):
    tax: float
    commission: float
    min_commission: float

    def get(self, c: Contract, ts: tp.Deque[td.Trade]) -> float:
        return sum([(t.num * t.price * c.value_per_dot * self.tax if t.order.oc == const.OC.C else 0) +
                    max(self.min_commission, t.num * t.price * c.value_per_dot * self.commission)
                    for t in ts])

    pass


@dc.dataclass
class Slippage(base.Msg):
    """
    be decided by exchange.
    """
    symbol: str

    def get(self, c: Contract, o: td.Order, price):
        raise NotImplementedError


@dc.dataclass
class SlippageFix(Slippage):
    step: float

    def get(self, c: Contract, o: td.Order, price) -> float:
        return price + (self.step if o.order_num > 0 else -self.step)

    pass


@dc.dataclass
class SlippagePer(Slippage):
    rate: float

    def get(self, c: Contract, o: td.Order, price) -> float:
        return price * (1 + self.rate * (1 if o.order_num > 0 else -1))

    pass
