import typing as t
import unittest
from collections import deque
from datetime import datetime

import numpy as np
import pandas as pd

import pyxq.actor
import pyxq.cb
import pyxq.msg
import pyxq.msg.md
import pyxq.msg.td
import pyxq.service
from pyxq import actor as s, const as c


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


class Strategy(pyxq.actor.GateWay):
    signal: MaSignal

    def __init__(self, broker: pyxq.cb.CallBack):
        super().__init__(broker=broker)
        self.signal = MaSignal(20)
        pass

    def on_kline(self, k: pyxq.msg.md.Kline):
        _x = self.signal.append(k.close)
        if _x > 0:
            self.broker.route(pyxq.msg.td.Order(
                symbol=k.symbol, oc=c.OC.O, price=k.close, num=100, dt=k.dt)
            )
        elif _x < 0:
            self.broker.route(pyxq.msg.td.Order(
                symbol=k.symbol, oc=c.OC.C, price=k.close, num=-100, dt=k.dt)
            )

    def on_trade(self, t: pyxq.msg.td.Trade):
        print(self.__class__.__name__, t.order.symbol, t.num, t.price)
        pass

    pass


def run():
    # 构建框架
    strategy = Strategy(broker=pyxq.cb.CallBack())
    exchange = pyxq.actor.Exchange(broker=pyxq.cb.CallBack())
    broker = pyxq.actor.Broker(gateway=strategy.broker, exchange=exchange.broker)
    # 读取数据
    symbol = '000002'
    data = pd.read_csv(rf'data/{symbol}.csv')
    # 行情事件
    for i, d in data[-100:].iterrows():
        exchange.broker.route(pyxq.msg.md.Kline(
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
