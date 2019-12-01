from pyxq import const as c
from pyxq.obj import Event


class Trade(Event):
    order_id: str
    symbol: str
    oc: c.OC
    price: float
    volume: float

    def __init__(self, order_id: str, symbol: str, oc: c.OC, price: float, volume: float):
        super().__init__()
        self.order_id = order_id
        self.symbol = symbol
        self.oc = oc
        self.price = price
        self.volume = volume

    pass


