import dataclasses as dc
import typing as tp
from collections import defaultdict

from .. import ba, cn
from ..msg import td, pa


@dc.dataclass
class Position(ba.Service, tp.Deque[td.Trade]):
    price: float = dc.field(init=False, default=0)

    def close(self, x: td.Trade, y: pa.ContractNewMod) -> float:
        self.price = x.price
        _volume = x.num
        _profit = 0
        _t = None
        _bs = -1 if x.num < 0 else 1
        while _volume * _bs > 0:
            if abs(self[0].num) > abs(_volume):
                _t = self[0]
                _t.num += _volume
                _profit += y.get_value(value=_volume * (x.price - _t.price))
                _volume = 0
            else:
                _t = self.popleft()
                _profit += y.get_value(value=_t.num * (x.price - _t.price))
                _volume += _t.num
        return _profit

    def open(self, x: td.Trade):
        self.price = x.price
        self.append(x)


@dc.dataclass
class Order(ba.Service, tp.Deque[td.Trade]):
    orq: td.OrderReq
    cancel_nm: float = dc.field(init=False, default=0)  # 取消
    reject_nm: float = dc.field(init=False, default=0)  # 拒绝

    @property
    def ing(self) -> float:
        return self.orq.od.num - (sum([i.num for i in self]) + self.cancel_nm + self.reject_nm)

    @property
    def ok(self) -> bool:
        return self.ing == 0

    pass


@dc.dataclass
class Account(ba.Service):
    """
    the account service.
    """
    cash: float = dc.field(default=0, init=False)
    contracts: tp.Dict[str, pa.ContractNewMod] = dc.field(default_factory=dict, init=False)
    commissions: tp.Dict[str, pa.CommissionMod] = dc.field(default_factory=dict, init=False)
    orders: tp.Dict[str, Order] = dc.field(default_factory=dict, init=False)
    positions: tp.DefaultDict[cn.LS, tp.DefaultDict[str, Position]] = dc.field(
        default_factory=lambda: defaultdict(lambda: defaultdict(Position)), init=False)

    @property
    def margin(self) -> float:
        return sum([
            self.contracts[symbol].get_margin(p.price * t.num)
            for ps in self.positions.values() for symbol, p in ps.items() for t in p
        ])

    @property
    def profit(self) -> float:
        return sum([
            self.contracts[symbol].get_value((p.price - t.price) * t.num)
            for ps in self.positions.values() for symbol, p in ps.items() for t in p
        ])

    @property
    def frozen(self) -> float:
        return sum([
            self.contracts[i.orq.od.s].get_margin(i.ing * i.orq.od.price)
            for i in self.orders.values() if i.orq.od.oc == cn.OC.O
        ])

    @property
    def equity(self) -> float:
        return self.cash + self.profit

    @property
    def free(self) -> float:
        return max(self.cash - self.frozen - self.margin + self.profit, 0)

    @property
    def pv(self) -> float:
        """

        :return: the positions value.
        """
        return sum([
            self.contracts[symbol].get_value(p.price * abs(t.num))
            for ps in self.positions.values() for symbol, p in ps.items() for t in p
        ])

    @property
    def commission(self) -> float:
        return sum([
            self.commissions[i.orq.od.s].get(c=self.contracts[i.orq.od.s], ts=i)
            for i in self.orders.values() if i.ok
        ])

    def get_free_position(self, s: str, ls: cn.LS) -> float:
        return (
            sum([t.num
                 for _ls, ps in self.positions.items() if _ls == ls
                 for _s, p in ps.items() if _s == s
                 for t in p]) -
            sum([o.ing
                 for o in self.orders.values() if o.orq.od.s == s and not o.ok])
        )

    pass
