import typing as tp
import unittest
from datetime import date, datetime
from os import path
import numpy as np
import pandas as pd

from pyxq import cn, actor, cb
from pyxq.msg import md, td, pa


class MaSignal(tp.Deque[float]):
    status: int

    def __init__(self, ml: tp.Optional[int] = ...):
        super().__init__(maxlen=ml)
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


class Strategy(actor.GateWay):
    signal: MaSignal
    cur_date: date

    def __init__(self, broker: cb.CallBack):
        super().__init__(broker=broker)
        self.signal = MaSignal(20)
        self.cur_date = date(year=1, month=1, day=1)
        pass

    def on_tick(self, x: md.Tick):
        if x.dt.date() != self.cur_date:
            self.cur_date = x.dt.date()
            _x = self.signal.append(x.price)
            if _x > 0:
                self.broker.route(td.OrderReq(od=td.OrderData(
                    symbol=x.symbol, oc=cn.OC.O, price=x.price, num=1000), dt=x.dt)
                )
            elif _x < 0:
                self.broker.route(td.OrderReq(od=td.OrderData(
                    symbol=x.symbol, oc=cn.OC.C, price=x.price, num=-1000), dt=x.dt)
                )

            pass

    def on_trade(self, t: td.Trade):
        print(self.__class__.__name__, t.orq.od.symbol, t.num, t.price)
        pass

    pass


def run():
    # 构建框架
    exchange = actor.Exchange(broker=cb.CallBack())
    strategy = Strategy(broker=cb.CallBack())
    broker = actor.Broker(gateway=strategy.broker, exchange=exchange.broker)
    # 配置
    cash, symbol = 100000, '000002'
    broker.on_cash(pa.Cash(num=cash, dt=datetime.now()))
    broker.on_contract(pa.ContractMsg(
        symbol=symbol, dt=datetime.now(), cm=pa.ContractMod(num_per_unit=100, value_per_dot=1, margin_ratio=1)))
    broker.on_commission(
        pa.CommissionMsg(
            dt=datetime.now(),
            symbol=symbol,
            cm=pa.CommissionStockA(tax=0.001, commission=0.00025, min_commission=5),
        ))
    # 读取数据
    symbol = '000002'
    file = path.join(path.dirname(path.realpath(__file__)), rf'data/{symbol}.csv')
    print(file)
    # data = pd.read_csv(path.abspath(f'data/{symbol}.csv'))
    # data = pd.read_csv(f'data/{symbol}.csv')
    data = pd.read_csv(file)
    # 行情事件
    for i, d in data[-100:].iterrows():
        _dt = datetime.strptime(d.timestamp, '%Y-%m-%d')
        exchange.on_open(md.Open(dt=_dt))
        exchange.on_tick(md.Tick(dt=_dt, symbol=symbol, price=d.open, volume=0))
        if d.close > d.open:
            exchange.on_tick(md.Tick(dt=_dt, symbol=symbol, price=d.low, volume=0))
            exchange.on_tick(md.Tick(dt=_dt, symbol=symbol, price=d.high, volume=0))
        else:
            exchange.on_tick(md.Tick(dt=_dt, symbol=symbol, price=d.high, volume=0))
            exchange.on_tick(md.Tick(dt=_dt, symbol=symbol, price=d.low, volume=0))

        exchange.on_tick(md.Tick(dt=_dt, symbol=symbol, price=d.close, volume=d.volume))
        _a = broker.acc
        print(_a.equity, _a.cash, _a.commission, _a.margin)
        exchange.on_close(md.Close(dt=_dt))


class TestService(unittest.TestCase):
    def test_strategy(self):
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
