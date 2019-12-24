from datetime import datetime
from unittest import TestCase

from pyxq import cn
from pyxq.msg import pa, td, md
from pyxq.service import account


class TestAccount(TestCase):
    def test_account(self):
        a = account.Account()
        cash, symbol = 100000, '000002'
        a.on_cash(pa.Cash(num=cash, dt=datetime.now()))
        a.on_contract(pa.ContractMsg(symbol=symbol, dt=datetime.now(),
                                     cm=pa.ContractMod(num_per_unit=100, value_per_dot=1, margin_ratio=1)))
        a.on_commission(
            pa.CommissionMsg(
                dt=datetime.now(),
                symbol=symbol,
                cm=pa.CommissionStockA(tax=0.001, commission=0.00025, min_commission=5),
            ))
        o = td.OrderReq(od=td.OrderData(symbol=symbol, oc=cn.OC.O, price=10, num=1000), dt=datetime.now())

        a.on_ordered(x=td.Ordered(orq=o, dt=datetime.now(), actor=cn.ACTOR.BROKER))
        self.assertTrue(a.frozen == 10 * 1000)
        a.on_trade(x=td.Trade(dt=datetime.now(), orq=o, price=o.od.price, num=o.od.num))
        self.assertTrue(
            a.frozen == 0 and
            a.cash == (cash - max(1000 * 10 * 0.00025, 5)) and
            a.margin == 1000 * 10 * 1
        )
        a.on_tick(x=md.Tick(symbol=symbol, dt=datetime.now(), price=20, volume=100))
        self.assertTrue(a.profit == (20 - 10) * 1000)

        o = td.OrderReq(od=td.OrderData(symbol=symbol, oc=cn.OC.C, price=20, num=-1000), dt=datetime.now())
        a.on_ordered(x=td.Ordered(orq=o, dt=datetime.now(), actor=cn.ACTOR.BROKER))
        a.on_trade(x=td.Trade(dt=datetime.now(), orq=o, price=o.od.price, num=o.od.num))
        self.assertTrue(
            a.frozen == 0 and
            a.margin == 0 and
            a.cash == (
                cash -
                max(1000 * 10 * 0.00025, 5) -  # 5
                1000 * 20 * 0.001 -  # 20
                max(1000 * 20 * 0.00025, 5) +  # 5
                (20 - 10) * 1000
            )
        )
        print('account pass!')
        pass
