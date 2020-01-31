import typing as tp
import unittest
from collections import defaultdict

import numpy as np

from pyxq import cn, actor, app
from pyxq.msg import md, td
from tests import msg


class MA(tp.Deque[float]):
    status: int
    cur_date: int

    def __init__(self, ml: tp.Optional[int] = ...):
        super().__init__(maxlen=ml)
        self.status = 0
        self.cur_date = ...
        pass

    def append(self, x: md.Tick) -> int:
        if x.dt.date() != self.cur_date:
            super().append(x.price)
            _mean = np.mean(self)
            if _mean > x.price and self.status > -1:
                self.status = -1
                return self.status
            elif _mean < x.price and self.status < 1:
                self.status = 1
                return self.status
            return 0
        else:
            return 0


class Strategy(actor.GateWay):
    signals: tp.DefaultDict[str, MA]
    contract_num: int

    def __init__(self, contract_num: int):
        self.signals = defaultdict(lambda: MA(20))
        self.contract_num = contract_num
        pass

    def on_tick(self, x: md.Tick):
        _sg = self.signals[x.s].append(x)
        if _sg > 0:
            _num = self.a.contracts[x.s].get_order_num(
                value=min(
                    self.a.equity * .9 / self.contract_num,
                    self.a.free / (self.contract_num - len(self.a.positions[cn.LS.L])),
                ),
                price=x.price
            )
            self.broker.route(td.OrderReq(od=td.Market(
                s=x.s, oc=cn.OC.O, price=x.price, num=_num),
                dt=x.dt)
            ) if _num > 0 else 0
        elif _sg < 0:
            _num = self.a.get_free_position(x.s, cn.LS.L)
            if _num > 0:
                self.broker.route(td.OrderReq(od=td.Market(
                    s=x.s, oc=cn.OC.C, price=x.price, num=-_num), dt=x.dt)
                )
        pass

    def on_close(self, x: md.Close):
        _a = self.a
        # print("权益:{:>14.2f} 可用:{:>14.2f} 保证:{:>10.2f} 冻结:{:>10.2f} 收益:{:>10.2f} 手续费:{:>5.2f} ".format(
        #     _a.equity, _a.free, _a.margin, _a.frozen, _a.profit, _a.commission, ))
        pass

    def on_trade(self, t: td.Trade):
        # print(t)
        pass

    def on_rejected(self, x: td.Rejected):
        raise UserWarning

    def on_canceled(self, x: td.Canceled):
        raise UserWarning

    pass


def test0():
    ap = app.A0(stg=Strategy(contract_num=len(msg.S)))
    list(ap.route(x=j) for i in msg.get_msg() for j in i)
    print(round(ap.a.equity, 2))
    assert round(ap.a.equity, 2) == 1492087.31
    return


class TestService(unittest.TestCase):
    def test_test0(self):
        test0()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
