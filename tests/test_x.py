from unittest import TestCase
from pyxq import callback as cb
from pyxq.obj import event


def _f1(trade: event.Trade):
    print("hello f1:", trade)
    pass


def _f2(kline: event.Kline):
    print("hello f2:", kline)
    pass


class TestX(TestCase):

    def test_test(self):
        _x = cb.CallBack()
        _x.bind(event.Kline.cls_key(), _f2)
        _x.bind(event.Trade.cls_key(), _f1)
        _x.route(event.Kline())
        _x.route(event.Trade())
        pass

    pass


if __name__ == '__main__':
    pass
