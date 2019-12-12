import pyxq.base
import pyxq.callback
from pyxq.msg import md, trade


class GateWay(pyxq.base.Actor):
    """
    中间网关/代理服务：对接行情和交易
    """
    broker: pyxq.callback.CallBack

    def __init__(self, broker: pyxq.callback.CallBack):
        broker.bind(md.Kline.key, self.on_kline)
        broker.bind(trade.Trade.key, self.on_trade)
        self.broker = broker
        pass

    def on_kline(self, k: md.Kline):
        pass

    def on_trade(self, t: trade.Trade):
        pass

    pass


class Broker(pyxq.base.Actor):
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
        gateway.bind(trade.Limit.key, self.on_order)
        exchange.bind(trade.Trade.key, self.on_trade)
        exchange.bind(md.Kline.key, self.on_kline)
        self.gateway = gateway
        self.exchange = exchange

    def on_order(self, o: trade.Limit):
        print(self.__class__.__name__, o)
        self.exchange.route(o)
        pass

    def on_trade(self, t: trade.Trade):
        print(self.__class__.__name__, t)
        self.gateway.route(t)
        pass

    def on_kline(self, k: md.Kline):
        self.gateway.route(k)
        pass

    pass


class Exchange(pyxq.base.Actor):
    """
    交易所，接受订单、交易撮合、发布行情
    """
    broker: pyxq.callback.CallBack

    def __init__(self, broker: pyxq.callback.CallBack):
        broker.bind(trade.Limit.key, self.on_order)
        self.broker = broker

    def on_order(self, o: trade.Limit):
        print(self.__class__.__name__, o)
        self.broker.route(
            trade.Trade(
                order_id=str(o.id),
                symbol=o.symbol,
                oc=o.oc,
                price=o.price,
                volume=o.order_num,
                dt=o.dt
            )
        )
        pass

    pass
