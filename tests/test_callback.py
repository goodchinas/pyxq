from unittest import TestCase
from pyxq import callback as cb
from pyxq.obj import event as e


def _order(order: e.Order):
    print('order:', order)
    pass


def _trade(trade: e.Trade):
    print('trade:', trade)


class TestCallBack(TestCase):
    def test_test(self):
        x = cb.CallBack()
        x.bind(e.Order.cls_key(), _order)
        x.bind(e.Trade.cls_key(), _trade)
        x.route(e.Order())
        x.route(e.Trade())
        x.unbind(e.Order.cls_key(), _order)
        x.route(e.Order())
        x.route(e.Trade())

    pass


if __name__ == '__main__':
    pass
