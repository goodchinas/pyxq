import unittest

import pyxq.callback
import pyxq.obj
import pyxq.obj.md
import pyxq.obj.order
import pyxq.obj.trade
from pyxq import service as s, callback as cb, const as c
from datetime import datetime
import pandas as pd
from collections import deque
import typing as t
import numpy as np


class MaSignal(deque):
    status: int

    def __init__(self, maxlen: t.Optional[int] = ...):
        super().__init__(maxlen=maxlen)
        self.status = 0
        pass

    def append(self, x) -> int:
        super().append(x)
        mean = np.mean(self)
        if mean > x and self.status > -1:
            self.status = -1
            return self.status
        elif mean < x and self.status < 1:
            self.status = 1
            return self.status
        return 0


class Strategy(s.GateWay):
    signal: MaSignal

    def __init__(self, broker: pyxq.callback.CallBack):
        super().__init__(broker=broker)
        self.signal = MaSignal(20)
        pass

    def on_kline(self, k: pyxq.obj.md.Kline):
        _x = self.signal.append(k.close)
        if _x > 0:
            self.broker.route(pyxq.obj.order.OrderEvent(pyxq.obj.order.OrderLimit(
                symbol=k.symbol, oc=c.OC.O, price=k.close, order_num=100, )
            ))
        elif _x < 0:
            self.broker.route(pyxq.obj.order.OrderEvent(pyxq.obj.order.OrderLimit(
                symbol=k.symbol, oc=c.OC.C, price=k.close, order_num=-100, )
            ))

    def on_trade(self, t: pyxq.obj.trade.Trade):
        print(self.__class__.__name__, t.symbol, t.volume, t.price)
        pass

    pass


def run():
    # 构建框架
    strategy = Strategy(broker=pyxq.callback.CallBack())
    exchange = s.Exchange(broker=pyxq.callback.CallBack())
    broker = s.Broker(gateway=strategy.broker, exchange=exchange.broker)
    # 读取数据
    symbol = '000002'
    data = pd.read_csv(f'data/{symbol}.csv')
    # 行情事件
    for i, d in data[-100:].iterrows():
        exchange.broker.route(pyxq.obj.md.Kline(
            symbol=symbol,
            dt=datetime.strptime(d.timestamp, '%Y-%m-%d'),
            open=d.open,
            high=d.high,
            low=d.low,
            close=d.close,
            volume=d.volume,
        ))


class TestService(unittest.TestCase):
    def test_run(self):
        run()
        self.assertTrue(True)

    def test_ma_signal(self):
        ma_signal = MaSignal(10)
        for i in np.random.random(20):
            _x = ma_signal.append(i)
            if _x != 0:
                print(_x)

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
