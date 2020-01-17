import itertools
import typing as tp
import unittest
from datetime import date, datetime

import numpy as np
import pandas as pd

from pyxq import cn, actor, cb
from pyxq.msg import md, td, pa
from pyxq.service import account


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

    def __init__(self, acc: account.Account, broker: cb.CallBackManager):
        super().__init__(acc=acc, broker=broker)
        self.signal = MaSignal(20)
        self.cur_date = date(year=1, month=1, day=1)
        pass

    def on_tick(self, x: md.Tick):
        if x.dt.date() != self.cur_date:
            self.cur_date = x.dt.date()
            _x = self.signal.append(x.price)
            if _x > 0:
                self.broker.route(td.OrderReq(od=td.Limit(
                    symbol=x.symbol, oc=cn.OC.O, price=x.price, num=1000), dt=x.dt)
                )
            elif _x < 0:
                self.broker.route(td.OrderReq(od=td.Limit(
                    symbol=x.symbol, oc=cn.OC.C, price=x.price, num=-1000), dt=x.dt)
                )

            pass

    def on_trade(self, t: td.Trade):
        # print(t)
        pass

    def on_rejected(self, x: td.Rejected):
        # print(x)
        pass

    pass


def test0():
    # 构建框架
    acc = account.Account()
    exchange = actor.Exchange(broker=cb.CallBackManager())
    strategy = Strategy(acc=acc, broker=cb.CallBackManager())
    broker = actor.Broker(acc=acc, gateway=strategy.broker, exchange=exchange.broker)
    # 参数项目
    start_date = datetime(year=2018, month=1, day=1)
    # 模拟行情
    np.random.seed(8)
    _n = 2000 * 24
    _s = [chr(_) for _ in range(ord('A'), ord("A") + 1)]
    _data = np.random.normal(loc=.0, scale=0.01, size=(_n, len(_s)))
    _data = np.exp(_data.cumsum(axis=0))
    _data = np.around(_data * np.tile(np.random.randint(low=1, high=200, size=len(_s)), reps=(_n, 1)), decimals=2)
    _dts = pd.date_range(start=start_date, periods=_n, freq='H')
    _is_new_day = itertools.chain([False], map(lambda x, y: x.date() != y.date(), _dts[1:], _dts[:-1]))
    _x = pd.DataFrame(
        data=_data,
        index=pd.date_range(start=start_date, periods=_n, freq='H'),
        columns=_s,
    )

    broker.on_cash(pa.Cash(num=1e8, dt=start_date))
    contract = pa.ContractMod(num_per_unit=100, value_per_dot=1, margin_ratio=1)
    commission = pa.CommissionStockA(tax=0.001, commission=0.00025, min_commission=5)
    list(map(lambda i: (
        broker.on_contract(x=pa.ContractMsg(
            symbol=i, dt=start_date, cm=contract,
        )),
        broker.on_commission(x=pa.CommissionMsg(
            symbol=i, dt=start_date, cm=commission,
        )),
    ), _s))
    _rank = np.arange(len(_s))
    _cur_dt = date(1, 1, 1)

    def _f(_dt, _row, _new_day):
        if _new_day:
            # _a = acc
            # print("权益:{:>14.2f} 可用:{:>14.2f} 保证:{:>10.2f} 冻结:{:>10.2f} 收益:{:>10.2f} 手续费:{:>5.2f} ".format(
            #     _a.equity, _a.free, _a.margin, _a.frozen, _a.profit, _a.commission, ))
            exchange.on_close(x=md.Close(dt=_dt.date()))
            exchange.on_open(x=md.Open(dt=_dt.date()))
        _r = np.random.permutation(_rank)
        for i in _r:
            exchange.on_tick(x=md.Tick(dt=_dt, symbol=_s[i], price=_row[i], volume=1000))

    list(map(lambda _dt, _row, _new_day: _f(_dt=_dt, _row=_row, _new_day=_new_day), _dts, _data, _is_new_day))
    _a = acc
    print("权益:{:>14.2f} 可用:{:>14.2f} 保证:{:>10.2f} 冻结:{:>10.2f} 收益:{:>10.2f} 手续费:{:>5.2f} ".format(
        _a.equity, _a.free, _a.margin, _a.frozen, _a.profit, _a.commission, ))

    return


class TestService(unittest.TestCase):
    def test_test0(self):
        test0()
        self.assertTrue(True)

    def test_ma_signal(self):
        ma_signal = MaSignal(10)
        for i in np.random.random(20):
            _x = ma_signal.append(i)
            # if _x != 0:
            #     print(_x)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
