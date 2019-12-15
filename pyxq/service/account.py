import dataclasses as dc
import typing as tp
from collections import defaultdict
from .. import base
from .. import const as ct
from ..msg import td, pa, md


@dc.dataclass
class Position(base.Service, tp.Deque[td.Trade]):
    symbol: str
    price: float = dc.field(init=False, default=0)
    frozen: float = dc.field(init=False, default=0)

    def close(self, x: td.Trade, y: pa.Contract) -> float:
        self.price = x.price
        self.frozen -= x.num
        _volume = x.num
        _profit = 0
        _t = None
        while _volume > 0:
            if abs(self[0].num) > abs(_volume):
                _t = self[0]
                _t.num -= _volume
                _profit += y.get_value(value=_volume * (x.price - _t.price))
                _volume = 0
            else:
                _t = self.popleft()
                _profit += y.get_value(value=_t.num * (x.price - _t.price))
                _volume -= _t.num
        return _profit

    def open(self, x: td.Trade) -> None:
        self.price = x.price
        self.append(x)

    def on_trade(self, x: td.Trade):
        if x.order.oc == ct.OC.C:
            self.frozen -= x.num

    def on_ordered(self, x: td.Ordered):
        if x.order.oc == ct.OC.C:
            self.frozen += x.order.order_num

    def on_canceled(self, x: td.Canceled):
        if x.order.oc == ct.OC.C:
            self.frozen -= x.num

    def on_rejected(self, x: td.Rejected):
        if x.order.oc == ct.OC.C:
            self.frozen -= x.num

    def get_profit(self, x: pa.Contract) -> float:
        return x.get_value(
            value=
            sum([t.num for t in self]) * self.price -
            sum([t.num * t.price for t in self])
        )

    def get_margin(self, x: pa.Contract) -> float:
        return x.get_margin(value=sum([t.num for t in self]) * self.price)


@dc.dataclass
class Order(base.Service, tp.Deque[td.Trade]):
    order: td.Order

    def on_trade(self, x: td.Trade) -> None:
        self.append(x)
        self.order.trade_num += x.num

    def on_rejected(self, x: td.Rejected) -> None:
        self.order.reject_nm += x.num

    def on_canceled(self, x: td.Canceled):
        self.order.cancel_nm += x.num

    def get_commission(self, x: pa.Commission, y: pa.Contract) -> float:
        return x.get(c=y, ts=self)

    def get_frozen(self, x: pa.Contract) -> float:
        return x.get_margin(
            value=self.ing * self.order.price
        ) if self.order.oc == ct.OC.O else 0.0

    @property
    def ing(self) -> float:
        return self.order.order_num - (self.order.trade_num + self.order.cancel_nm + self.order.reject_nm)

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
    positions: tp.DefaultDict[float, tp.Dict[str, Position]] = dc.field(
        default_factory=lambda: defaultdict(dict), init=False)

    @property
    def margin(self) -> float:
        return sum([p.get_margin(x=self.contracts[p.symbol]) for i in self.positions.values() for p in i.values()])

    @property
    def profit(self) -> float:
        return sum([p.get_profit(x=self.contracts[p.symbol]) for i in self.positions.values() for p in i.values()])

    @property
    def frozen(self):
        return sum([i.get_frozen(x=self.contracts[i.order.symbol]) for i in self.orders.values()])

    @property
    def equity(self) -> float:
        return self.cash + self.profit

    @property
    def free(self) -> float:
        return self.cash - self.frozen - self.margin + self.profit

    @property
    def commission(self) -> float:
        return sum([
            i.get_commission(x=self.commissions[i.order.symbol], y=self.contracts[i.order.symbol])
            for i in self.orders.values() if i.ok
        ])

    def settle(self, x: td.Settle):
        _r = td.Settled(cash=self.free, equity=self.equity, commission=self.commission, dt=x.dt)
        self.orders = {k: v for k, v in self.orders.items() if not v.ok}
        return _r

    def on_ordered(self, x: td.Ordered):
        self.orders[x.order.id] = Order(order=x.order)
        if x.order.oc == ct.OC.C:
            self.positions[x.order.bs][x.order.symbol].on_ordered(x=x)

    def on_trade(self, x: td.Trade):
        if x.order.symbol not in self.positions[x.bs]:
            self.positions[x.bs][x.order.symbol] = Position(symbol=x.order.symbol)
        _position = self.positions[x.bs][x.order.symbol]
        if x.order.oc == ct.OC.O:
            _position.open(x=x)
        else:
            self.cash += _position.close(x=x, y=self.contracts[x.order.symbol])
            _position.on_trade(x=x)
            if len(_position) == 0:
                del self.positions[x.bs][x.order.symbol]
        self.orders[x.order.id].on_trade(x)

        self._order_rtn(x.order)

    def on_canceled(self, x: td.Canceled):
        self.orders[x.order.id].on_canceled(x)
        self._order_rtn(x.order)
        if x.order.oc == ct.OC.C:
            self.positions[x.order.bs][x.order.symbol].on_canceled(x=x)

    def on_rejected(self, x: td.Rejected):
        self.orders[x.order.id].on_rejected(x)
        self._order_rtn(x.order)
        if x.order.oc == ct.OC.C:
            self.positions[x.order.bs][x.order.symbol].on_rejected(x=x)

    def _order_rtn(self, x: td.Order):
        if self.orders[x.id].ok:
            self.cash -= self.orders[x.id].get_commission(x=self.commissions[x.symbol],
                                                          y=self.contracts[x.symbol])

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
