import pyxq.callback
import pyxq.obj
import pyxq.obj.base
import pyxq.obj.md
import pyxq.obj.order
import pyxq.obj.trade
from .. import callback as cb
import typing as t


class GateWay(object):
    """
    中间网关/代理服务：对接行情和交易
    """
    broker: pyxq.callback.CallBack

    def __init__(self, broker: pyxq.callback.CallBack):
        broker.bind(pyxq.obj.md.Kline.cls_key(), self.on_kline)
        broker.bind(pyxq.obj.trade.Trade.cls_key(), self.on_trade)
        self.broker = broker
        pass

    def on_kline(self, k: pyxq.obj.md.Kline):
        pass

    def on_trade(self, t: pyxq.obj.trade.Trade):
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
    gateway: pyxq.callback.CallBack
    exchange: pyxq.callback.CallBack

    def __init__(self, gateway: pyxq.callback.CallBack, exchange: pyxq.callback.CallBack):
        gateway.bind(pyxq.obj.order.OrderEvent.cls_key(), self.on_order)
        exchange.bind(pyxq.obj.trade.Trade.cls_key(), self.on_trade)
        exchange.bind(pyxq.obj.md.Kline.cls_key(), self.on_kline)
        self.gateway = gateway
        self.exchange = exchange

    def on_order(self, o: pyxq.obj.order.OrderEvent):
        print(self.__class__.__name__, o)
        self.exchange.route(o)
        pass

    def on_trade(self, t: pyxq.obj.trade.Trade):
        print(self.__class__.__name__, t)
        self.gateway.route(t)
        pass

    def on_kline(self, k: pyxq.obj.md.Kline):
        self.gateway.route(k)
        pass

    pass


class Exchange(object):
    """
    交易所，接受订单、交易撮合、发布行情
    """
    broker: pyxq.callback.CallBack

    def __init__(self, broker: pyxq.callback.CallBack):
        broker.bind(pyxq.obj.order.OrderEvent.cls_key(), self.on_order)
        self.broker = broker

    def on_order(self, o: pyxq.obj.order.OrderEvent):
        print(self.__class__.__name__, o)
        om = o.om
        if type(om) is not pyxq.obj.order.OrderLimit:
            return
        self.broker.route(
            pyxq.obj.trade.Trade(
                order_id=o.id,
                symbol=om.symbol,
                oc=om.oc,
                price=om.price,
                volume=om.order_num,
            )
        )
        pass

    pass
