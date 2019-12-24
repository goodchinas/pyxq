import typing as tp
from collections import deque
from .. import ba, cb, itf, cn
from ..msg import md, td, pa
from ..service import account


class GateWay(ba.Actor, itf.IMDRtn, itf.IOrderRsp):
    """
    中间网关/代理服务：对接行情和交易
    """
    broker: cb.CallBack

    def __init__(self, broker: cb.CallBack):
        broker.bind(td.Trade.key, self.on_trade)
        broker.bind(td.Ordered.key, self.on_ordered)
        broker.bind(td.Canceled.key, self.on_canceled)
        broker.bind(td.Rejected.key, self.on_rejected)
        broker.bind(md.Open.key, self.on_open)
        broker.bind(md.Close.key, self.on_close)
        broker.bind(md.Tick.key, self.on_tick)
        broker.bind(md.OrderBook.key, self.on_order_book)
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

    pass


class Broker(ba.Actor, itf.IOrderReq, itf.IOrderRsp, itf.IPaReq, itf.IMDRtn):
    """
    账户维护：网关/代理右侧，模拟类服务。
    订单、仓位、资产和绩效分析
    存储仓位，不需要存储委托和成交（缓存都数据中心一份）
    """
    gateway: cb.CallBack
    exchange: cb.CallBack
    acc: account.Account

    def __init__(self, gateway: cb.CallBack, exchange: cb.CallBack):
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
        self.gateway = gateway
        self.exchange = exchange
        self.acc = account.Account()

    def on_cash(self, x: pa.Cash):
        self.acc.on_cash(x=x)

    def on_commission(self, x: pa.CommissionMsg):
        self.acc.on_commission(x=x)

    def on_contract(self, x: pa.ContractMsg):
        self.acc.on_contract(x=x)

    def on_order(self, o: td.OrderReq):
        _od = o.od
        _cn = self.acc.contracts[_od.symbol]
        _cm = self.acc.commissions[_od.symbol]
        _x = True
        if _od.oc == cn.OC.O:
            if self.acc.free < (
                _cn.get_margin(value=_od.price * _od.num) +
                _cm.get(c=_cn, ts=deque([td.Trade(dt=..., orq=o, price=_od.price, num=_od.num)]))
            ):
                _x = False
        else:
            if abs(self.acc.get_free(symbol=_od.symbol, ls=_od.ls)) < abs(_od.num):
                _x = False
        if _x:
            _ordered = td.Ordered(dt=o.dt, orq=o, actor=cn.ACTOR.BROKER)
            self.acc.on_ordered(x=_ordered)
            self.gateway.route(x=_ordered)
            self.exchange.route(x=o)
        else:
            self.gateway.route(x=td.Rejected(dt=o.dt, orq=o, actor=cn.ACTOR.BROKER))
        pass

    def on_cancel(self, x: td.Cancel):
        self.exchange.route(x=x)
        pass

    def on_ordered(self, x: td.Ordered):
        self.gateway.route(x=x)

    def on_canceled(self, x: td.Canceled):
        self.acc.on_canceled(x=x)
        self.gateway.route(x=x)

    def on_rejected(self, x: td.Rejected):
        self.acc.on_rejected(x=x)
        self.gateway.route(x=x)
        pass

    def on_trade(self, t: td.Trade):
        self.acc.on_trade(t)
        self.gateway.route(x=t)
        pass

    def on_open(self, x: md.Open):
        self.acc.on_open(x=x)
        self.gateway.route(x=x)
        pass

    def on_close(self, x: md.Close):
        self.acc.on_close(x=x)
        self.gateway.route(x=x)
        pass

    def on_tick(self, x: md.Tick):
        self.acc.on_tick(x=x)
        self.gateway.route(x)
        pass

    def on_order_book(self, x: md.OrderBook):
        self.acc.on_order_book(x=x)
        self.gateway.route(x=x)
        pass

    pass


class Exchange(ba.Actor, itf.IOrderReq, itf.IMDRtn):
    """
    交易所，接受订单、交易撮合、发布行情
    """
    broker: cb.CallBack
    orders: tp.Deque[td.OrderReq]

    def __init__(self, broker: cb.CallBack):
        broker.bind(td.OrderReq.key, self.on_order)
        broker.bind(td.Cancel.key, self.on_cancel)
        self.broker = broker
        self.orders = deque()

    def on_order(self, x: td.OrderReq):
        self.broker.route(td.Ordered(dt=x.dt, orq=x, actor=cn.ACTOR.EXCHANGE))
        self.orders.append(x)
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
        while len(self.orders) > 0:
            _o = self.orders.popleft()
            self.broker.route(td.Trade(
                dt=x.dt,
                orq=_o,
                price=x.price,
                num=_o.od.num,
            ))
        self.broker.route(x)
        pass

    def on_order_book(self, x: md.OrderBook):
        self.broker.route(x)
        pass

    pass
