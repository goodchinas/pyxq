"""
the actor model.
"""
import typing as tp
from collections import deque, defaultdict

from .. import ba, cb, itf, cn
from ..msg import md, td, pa
from ..service import account


class GateWay(ba.Actor, itf.IMDRtn, itf.IOrderRsp, itf.IFactor, itf.IGateWayInit):
    """
    the local gateway father class.
    """
    a: account.Account
    broker: cb.CallBackManager
    center: cb.CallBackManager

    def init(self, a: account.Account, center: cb.CallBackManager, broker: cb.CallBackManager):
        center.bind(md.Factor.key, self.on_factor)
        broker.bind(td.Trade.key, self.on_trade)
        broker.bind(td.Ordered.key, self.on_ordered)
        broker.bind(td.Canceled.key, self.on_canceled)
        broker.bind(td.Rejected.key, self.on_rejected)
        broker.bind(md.Open.key, self.on_open)
        broker.bind(md.Close.key, self.on_close)
        broker.bind(md.Tick.key, self.on_tick)
        broker.bind(md.OrderBook.key, self.on_order_book)
        self.a = a
        self.center = center
        self.broker = broker
        pass

    def on_trade(self, t: td.Trade):
        pass

    def on_ordered(self, x: td.Ordered):
        pass

    def on_canceled(self, x: td.Canceled):
        pass

    def on_rejected(self, x: td.Rejected):
        pass

    def on_open(self, x: md.Open):
        pass

    def on_close(self, x: md.Close):
        pass

    def on_tick(self, x: md.Tick):
        pass

    def on_order_book(self, x: md.OrderBook):
        pass

    def on_factor(self, x: md.Factor):
        pass

    pass


class Broker(ba.Actor, itf.IOrderReq, itf.IOrderRsp, itf.IPaReq, itf.IMDRtn):
    """
    the broker actor that account service.
    """
    a: account.Account
    center: cb.CallBackManager
    gateway: cb.CallBackManager
    exchange: cb.CallBackManager

    def __init__(self, a: account.Account,
                 center: cb.CallBackManager,
                 gateway: cb.CallBackManager,
                 exchange: cb.CallBackManager):
        center.bind(pa.ContractDelMsg.key, self.on_contract_del)
        center.bind(pa.ContractNewMsg.key, self.on_contract_new)
        center.bind(pa.CommissionMsg.key, self.on_commission)
        center.bind(pa.Cash.key, self.on_cash)
        gateway.bind(td.OrderReq.key, self.on_order)
        gateway.bind(td.Cancel.key, self.on_cancel)
        exchange.bind(td.Ordered.key, self.on_ordered)
        exchange.bind(td.Trade.key, self.on_trade)
        exchange.bind(td.Canceled.key, self.on_canceled)
        exchange.bind(td.Rejected.key, self.on_rejected)
        exchange.bind(md.Open.key, self.on_open)
        exchange.bind(md.Close.key, self.on_close)
        exchange.bind(md.Tick.key, self.on_tick)
        exchange.bind(md.OrderBook.key, self.on_order_book)
        self.a = a
        self.center = center
        self.gateway = gateway
        self.exchange = exchange

    def on_cash(self, x: pa.Cash):
        self.a.cash += x.num

    def on_commission(self, x: pa.CommissionMsg):
        self.a.commissions[x.s] = x.cm

    def on_contract_new(self, x: pa.ContractNewMsg):
        self.a.contracts[x.s] = x.cm

    def on_contract_del(self, x: pa.ContractDelMsg):
        del self.a.contracts[x.s]

    def on_order(self, o: td.OrderReq):
        _od = o.od
        _cn = self.a.contracts[_od.s]
        _cm = self.a.commissions[_od.s]
        _x = True

        if (
            _od.num == 0 or  # zero number not be allowed.
            (_od.oc == cn.OC.C and abs(self.a.get_free_position(s=_od.s, ls=_od.ls)) < abs(_od.num))
        ):
            _x = False
        if _x:
            self.a.orders[o.id] = account.Order(orq=o)
            self.gateway.route(x=td.Ordered(dt=o.dt, orq=o))
            self.exchange.route(x=o)
        else:
            self.gateway.route(x=td.Rejected(dt=o.dt, orq=o))
        pass

    def on_cancel(self, x: td.Cancel):
        self.exchange.route(x=x)
        pass

    def on_ordered(self, x: td.Ordered):
        self.gateway.route(x=x)

    def on_canceled(self, x: td.Canceled):
        self.a.orders[x.orq.id].cancel_nm = self.a.orders[x.orq.id].ing
        self._on_order_rsp(x.orq)
        self.gateway.route(x=x)

    def on_rejected(self, x: td.Rejected):
        self.a.orders[x.orq.id].reject_nm = self.a.orders[x.orq.id].ing
        self._on_order_rsp(x.orq)
        self.gateway.route(x=x)
        pass

    def on_trade(self, x: td.Trade):
        acc = self.a
        if x.orq.od.oc == cn.OC.O:
            acc.positions[x.ls][x.orq.od.s].open(x=x)
        else:
            _p = acc.positions[x.ls][x.orq.od.s]
            acc.cash += _p.close(x=x, y=acc.contracts[x.orq.od.s])
            if len(_p) == 0:
                del acc.positions[x.ls][x.orq.od.s]
        acc.orders[x.orq.id].append(x)
        self._on_order_rsp(x.orq)
        self.gateway.route(x=x)
        pass

    def _on_order_rsp(self, x: td.OrderReq):
        acc = self.a
        if acc.orders[x.id].ok:
            acc.cash -= acc.commissions[x.od.s].get(c=acc.contracts[x.od.s], ts=acc.orders[x.id])

    def on_open(self, x: md.Open):
        self.gateway.route(x=x)
        pass

    def on_close(self, x: md.Close):
        self.gateway.route(x=x)
        self.a.orders = {k: v for k, v in self.a.orders.items() if not v.ok}
        pass

    def on_tick(self, x: md.Tick):
        for i in self.a.positions.values():
            if x.s in i:
                i[x.s].price = x.price
        self.gateway.route(x)
        pass

    def on_order_book(self, x: md.OrderBook):
        self.gateway.route(x=x)
        pass

    pass


class Exchange(ba.Actor, itf.IOrderReq, itf.IMDRtn):
    """
    the exchange actor.
    """
    center: cb.CallBackManager
    broker: cb.CallBackManager
    orders: tp.DefaultDict[str, tp.DefaultDict[cn.BS, tp.Deque[td.OrderReq]]]
    ticks: tp.Dict[str, md.Tick]

    def __init__(self, center: cb.CallBackManager, broker: cb.CallBackManager):
        center.bind(md.Tick.key, self.on_tick)
        center.bind(md.OrderBook.key, self.on_order_book)
        center.bind(md.Open.key, self.on_open)
        center.bind(md.Close.key, self.on_close)
        broker.bind(td.OrderReq.key, self.on_order)
        broker.bind(td.Cancel.key, self.on_cancel)
        self.center = center
        self.broker = broker
        self.orders = defaultdict(lambda: defaultdict(deque))
        self.ticks = dict()

    def _order_match(self, o: td.OrderReq, p: float):
        _t = type(o.od)
        if _t == td.Limit:
            if (
                (o.od.price >= p and o.od.bs == cn.BS.B) or
                (o.od.price <= p and o.od.bs == cn.BS.S)
            ):
                self.broker.route(x=td.Trade(dt=o.dt, orq=o, price=p, num=o.od.num, ))
            else:
                self.orders[o.od.s][o.od.bs].append(o)
        elif _t == td.Market:
            self.broker.route(x=td.Trade(dt=o.dt, orq=o, price=p, num=o.od.num, ))

    def on_order(self, x: td.OrderReq):
        self.broker.route(td.Ordered(dt=x.dt, orq=x))
        if x.od.s in self.ticks:
            self._order_match(o=x, p=self.ticks[x.od.s].price)
        else:
            self.orders[x.od.s][x.od.bs].append(x)
        pass

    def on_cancel(self, x: td.Cancel):
        pass

    def on_open(self, x: md.Open):
        self.broker.route(x)
        pass

    def on_close(self, x: md.Close):
        self.broker.route(x)
        pass

    def on_tick(self, x: md.Tick):
        self.ticks[x.s] = x
        if x.s in self.orders:
            for bs, v in self.orders[x.s].items():
                self.orders[x.s][bs] = deque()
                for o in v:
                    self._order_match(o=o, p=x.price)
        self.broker.route(x)
        pass

    def on_order_book(self, x: md.OrderBook):
        self.broker.route(x)
        pass

    pass
