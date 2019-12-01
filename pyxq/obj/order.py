from pyxq import const as c
from . import base


class OrderModel(base.Model):
    symbol: str
    oc: c.OC
    order_num: float
    trade_num: float
    cancel_nm: float

    def __init__(self, symbol: str,
                 oc: c.OC,
                 order_num: float, ):
        super().__init__()
        self.symbol = symbol
        self.oc = oc
        self.order_num = order_num
        self.trade_num = 0
        self.cancel_nm = 0

    pass


class OrderLimit(OrderModel):
    symbol: str
    oc: c.OC
    order_num: float
    price: float

    def __init__(self, symbol: str = ..., oc: c.OC = ..., order_num: float = ..., price: float = ...):
        super().__init__(symbol=symbol, oc=oc, order_num=order_num)
        self.price=price

    pass


class OrderMarket(OrderModel):
    pass


class OrderEvent(base.Event):
    om: OrderModel

    def __init__(self, om: OrderModel):
        super().__init__()
        self.om = om

    pass
