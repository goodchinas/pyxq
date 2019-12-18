import typing as tp

from .. import base
from .. import cb
from ..msg import md, td, pa
from ..service import account


class GateWay(base.Actor):
    """
    中间网关/代理服务：对接行情和交易
    """
    broker: cb.CallBack

    def __init__(self, broker: cb.CallBack):
        broker.bind(md.Kline.key, self.on_kline)
        broker.bind(td.Trade.key, self.on_trade)
        self.broker = broker
        pass

    def on_kline(self, k: md.Kline):
        pass

    def on_trade(self, t: td.Trade):
        pass

    pass


class KLine(base.Actor):
    broker: cb.CallBack
    gateway: cb.CallBack
    ks: tp.Dict[str, md.Kline]

    def __init__(self, broker: cb.CallBack, gateway: cb.CallBack):
        broker.bind(md.Tick.key, self.on_tick)
        self.broker = broker
        self.gateway = gateway

    def on_tick(self, x: md.Tick):
        _p = x.trade.price
        if x.symbol not in self.ks or self.ks[x.symbol].dt.date() != x.dt.date():
            self.ks[x.symbol] = md.Kline(symbol=x.symbol, dt=x.dt, open=_p, high=_p, low=_p,
                                         close=_p, volume=x.trade.num)
        else:
            _k = self.ks[x.symbol]
            _k.high = max(_k.high, _p)
            _k.low = min(_k.low, _p)
            _k.close = _p
            _k.volume += x.trade.num
        pass

    def on_settle(self, x: td.Settle):
        for i in self.ks.values():
            i.dt = x.dt
            self.gateway.route(i)


class Broker(base.Actor):
    """
    账户维护：网关/代理右侧，模拟类服务。
    订单、仓位、资产和绩效分析
    存储仓位，不需要存储委托和成交（缓存都数据中心一份）
    """
    gateway: cb.CallBack
    exchange: cb.CallBack
    acc: account.Account

    def __init__(self, gateway: cb.CallBack, exchange: cb.CallBack):
        gateway.bind(td.OrderMsg.key, self.on_order)
        exchange.bind(td.Trade.key, self.on_trade)
        exchange.bind(md.Kline.key, self.on_kline)
        self.gateway = gateway
        self.exchange = exchange
        self.acc = account.Account()

    def on_canceled(self, x: td.Canceled):
        self.acc.on_canceled(x=x)

    def on_cash(self, x: pa.Cash):
        self.acc.on_cash(x=x)

    def on_commission(self, x: pa.CommissionMsg):
        self.acc.on_commission(x=x)

    def on_contract(self, x: pa.ContractMsg):
        self.acc.on_contract(x=x)

    def on_ordered(self, x: td.Ordered):
        self.acc.on_ordered(x=x)

    # def on

    def on_order(self, o: td.OrderMsg):
        print(self.__class__.__name__, o)
        self.exchange.route(o)
        pass

    def on_trade(self, t: td.Trade):
        print(self.__class__.__name__, t)
        self.gateway.route(t)
        pass

    def on_kline(self, k: md.Kline):
        self.gateway.route(k)
        pass

    pass


class Exchange(base.Actor):
    """
    交易所，接受订单、交易撮合、发布行情
    """
    broker: cb.CallBack

    def __init__(self, broker: cb.CallBack):
        broker.bind(td.OrderMsg.key, self.on_order)
        self.broker = broker

    def on_order(self, o: td.OrderMsg):
        print(self.__class__.__name__, o)
        self.broker.route(
            td.Trade(
                oms=o,
                price=o.od.price,
                num=o.od.num,
                dt=o.dt
            )
        )
        pass

    pass
