import unittest

from pyxq import cn, actor, app
from pyxq.msg import md, td
from tests import msg
from tests.msg import F


class Strategy(actor.GateWay):
    factors: dict
    today_last_ticks: dict
    buys: set
    sells: set
    top: int
    ratio: float
    period: int
    days: int

    def __init__(self):
        self.factors = dict()
        self.today_last_ticks = {}
        self.buys = set()
        self.sells = set()
        self.top = 10
        self.ratio = 1
        self.period = 30
        self.days = 0
        pass

    def on_tick(self, x: md.Tick):
        if x.s in self.today_last_ticks:
            return
        self.today_last_ticks[x.s] = x
        if x.s in self.sells:  # no sell completed
            list((
                     self.sells.remove(x.s),
                     self.broker.route(x=td.OrderReq(dt=x.dt, od=td.Market(
                         s=i, oc=cn.OC.C, price=self.today_last_ticks[i].price,
                         num=-self.a.get_free_position(s=i, ls=cn.LS.L),
                     ))),
                 )
                 for i in (self.sells & set(self.today_last_ticks))
                 )
        elif (
            len(self.buys) > 0 and
            set(self.buys) - set(self.today_last_ticks) == set() and
            len([o for o in self.a.orders.values() if not o.ok and o.orq.od.oc == cn.OC.C]) == 0
        ):
            _cash = min(self.a.equity * self.ratio / self.top, self.a.free / len(self.buys))
            _cur = set(self.today_last_ticks)
            _nums = map(lambda i: (
                i,
                self.a.contracts[i].get_order_num(value=_cash, price=self.today_last_ticks[i].price, ),
            ), self.buys & _cur)
            self.buys -= _cur
            list(map(
                lambda i: self.broker.route(td.OrderReq(dt=x.dt, od=td.Market(
                    s=i[0], oc=cn.OC.O, price=self.today_last_ticks[i[0]].price, num=i[1],
                ))),
                filter(lambda i: i[1] > 0, _nums)
            ))

    def on_factor(self, x: md.Factor):
        self.factors[x.s] = F(**x.data)
        pass

    def on_close(self, x: md.Close):
        self.today_last_ticks.clear()
        # _a = self.a
        # print("权益:{:>14.2f} 可用:{:>14.2f} 保证:{:>10.2f} 冻结:{:>10.2f} 收益:{:>10.2f} 手续费:{:>5.2f} ".format(
        #     _a.equity, _a.free, _a.margin, _a.frozen, _a.profit, _a.commission, ))
        pass

    def on_open(self, x: md.Open):
        def _f(f: F):
            return f.x

        _r = list(map(
            lambda x: x[0],
            sorted(
                filter(lambda x: _f(x[1]) is not None,
                       self.factors.items()),
                key=lambda x: _f(x[1]), reverse=True),
        ))
        hold, top = set(self.a.positions[cn.LS.L]), set(_r[:self.top])
        self.days += 1
        if self.days % self.period == 0:
            self.sells, self.buys = hold - top, top - hold
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
    ap = app.A0(stg=Strategy())
    list(ap.route(x=j) for i in msg.get_msg() for j in i)
    print(round(ap.a.equity, 2))
    assert round(ap.a.equity, 2) == 7696159.92
    return


class TestService(unittest.TestCase):
    def test_test0(self):
        test0()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
