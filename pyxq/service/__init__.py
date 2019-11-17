from ..obj import event as e
from .. import callback as cb
import typing as t
from .. import const as c


class GateWay(object):
    """
    中间网关/代理服务：对接行情和交易
    """
    broker: cb.CallBack

    def __init__(self, broker: cb.CallBack):
        broker.bind(e.Kline.cls_key(), self.on_kline)
        broker.bind(e.Trade.cls_key(), self.on_trade)
        self.broker = broker
        pass

    def on_kline(self, k: e.Kline):
        pass

    def on_trade(self, t: e.Trade):
        pass

    pass


class Broker(object):
    """
    账户维护：网关/代理右侧，模拟类服务。
    订单、仓位、资产和绩效分析
    存储仓位，不需要存储委托和成交（缓存都数据中心一份）
    todo **账户服务，多账户数据**
        维护账户（组），绩效分析的模块
    """
    gateway: cb.CallBack
    exchange: cb.CallBack

    def __init__(self, gateway: cb.CallBack, exchange: cb.CallBack):
        gateway.bind(e.Order.cls_key(), self.on_order)
        exchange.bind(e.Trade.cls_key(), self.on_trade)
        exchange.bind(e.Kline.cls_key(), self.on_kline)
        self.gateway = gateway
        self.exchange = exchange

    def on_order(self, o: e.Order):
        print(self.__class__.__name__, o)
        self.exchange.route(o)
        pass

    def on_trade(self, t: e.Trade):
        print(self.__class__.__name__, t)
        self.gateway.route(t)
        pass

    def on_kline(self, k: e.Kline):
        print(self.__class__.__name__, k)
        self.gateway.route(k)
        pass

    pass


class Exchange(object):
    """
    交易所，接受订单、交易撮合、发布行情
    """
    broker: cb.CallBack

    def __init__(self, broker: cb.CallBack):
        broker.bind(e.Order.cls_key(), self.on_order)
        self.broker = broker

    def on_order(self, o: e.Order):
        print(self.__class__.__name__, o)
        self.broker.route(
            e.Trade(
                order_id=o.id,
                symbol=o.symbol,
                bs=o.bs,
                ls=o.oc,
                price=o.price,
                volume=o.volume,
            )
        )
        pass

    def run(self, data: t.List[e.Event]):
        for d in data:
            self.broker.route(d)
        pass

    pass
