import dataclasses as dc
import typing as tp
from collections import defaultdict
from .. import base
from .. import const as ct
from ..msg import td, pa, md


@dc.dataclass
class Position(base.Service, tp.Deque[td.Trade]):
    price: float = dc.field(init=False, default=0)

    def close(self, x: td.Trade, y: pa.Contract) -> float:
        self.price = x.price
        _volume = x.num
        _profit = 0
        _t = None
        while _volume * x.bs > 0:
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

    def open(self, x: td.Trade) -> None:
        self.price = x.price
        self.append(x)


@dc.dataclass
class Order(base.Service, tp.Deque[td.Trade]):
    order: td.Order
    cancel_nm: float = dc.field(init=False, default=0)  # 取消
    reject_nm: float = dc.field(init=False, default=0)  # 拒绝

    @property
    def ing(self) -> float:
        return self.order.num - (sum([i.num for i in self]) + self.cancel_nm + self.reject_nm)

    @property
    def ok(self) -> bool:
        return self.ing == 0

    pass


@dc.dataclass
class Account(base.Service):
    """
    持仓、权益、处理成交
    # todo 更新行情，另起一个事件
        监控信息流，记录委托成交等信息
    """
    cash: float = dc.field(default=0, init=False)
    contracts: tp.Dict[str, pa.Contract] = dc.field(default_factory=dict, init=False)
    commissions: tp.Dict[str, pa.Commission] = dc.field(default_factory=dict, init=False)
    orders: tp.Dict[str, Order] = dc.field(default_factory=dict, init=False)
    positions: tp.DefaultDict[float, tp.DefaultDict[str, Position]] = dc.field(
        default_factory=lambda: defaultdict(lambda: defaultdict(Position)), init=False)

    @property
    def margin(self) -> float:
        return sum([
            self.contracts[t.order.symbol].get_margin(t.price * t.num)
            for i in self.positions.values() for p in i.values() for t in p
        ])

    @property
    def profit(self) -> float:
        return sum([
            self.contracts[t.order.symbol].get_value((p.price - t.price) * t.num)
            for i in self.positions.values() for p in i.values() for t in p
        ])

    @property
    def frozen(self):
        return sum([
            self.contracts[i.order.symbol].get_margin(i.ing * i.order.price)
            for i in self.orders.values() if i.order.oc == ct.OC.O
        ])


    @property
    def equity(self) -> float:
        return self.cash + self.profit

    @property
    def free(self) -> float:
        return self.cash - self.frozen - self.margin + self.profit

    @property
    def commission(self) -> float:
        return sum([
            self.commissions[i.order.symbol].get(c=self.contracts[i.order.symbol], ts=i)
            for i in self.orders.values() if i.ok
        ])

    def settle(self, x: td.Settle):
        _r = td.Settled(cash=self.free, equity=self.equity, commission=self.commission, dt=x.dt)
        self.orders = {k: v for k, v in self.orders.items() if not v.ok}
        return _r

    def on_ordered(self, x: td.Ordered):
        self.orders[x.order.id] = Order(order=x.order)

    def on_trade(self, x: td.Trade):
        if x.order.oc == ct.OC.O:
            self.positions[x.bs][x.order.symbol].open(x=x)
        else:
            _p = self.positions[-x.bs][x.order.symbol]
            self.cash += _p.close(x=x, y=self.contracts[x.order.symbol])
            if len(_p) == 0:
                del self.positions[-x.bs][x.order.symbol]
        self.orders[x.order.id].append(x)
        self._order_rtn(x.order)

    def on_canceled(self, x: td.Canceled):
        self.orders[x.order.id].cancel_nm += x.num
        self._order_rtn(x.order)

    def on_rejected(self, x: td.Rejected):
        self.orders[x.order.id].reject_nm += x.num
        self._order_rtn(x.order)

    def _order_rtn(self, x: td.Order):
        if self.orders[x.id].ok:
            self.cash -= self.commissions[x.symbol].get(c=self.contracts[x.symbol], ts=self.orders[x.id])

    def on_tick(self, x: md.Tick):
        for i in self.positions.values():
            if x.symbol in i:
                i[x.symbol].price = x.price

    def on_cash(self, x: pa.Cash):
        self.cash += x.num

    def on_contract(self, x: pa.Contract):
        self.contracts[x.symbol] = x

    def on_commission(self, x: pa.Commission):
        self.commissions[x.symbol] = x

    pass
