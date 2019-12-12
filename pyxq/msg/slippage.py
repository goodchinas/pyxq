import dataclasses as dc

import pyxq.base
from . import contract, trade


@dc.dataclass
class Slippage(pyxq.base.Msg):
    def get_price(self, c: contract.Contract, o: trade.Order, price):
        raise NotImplementedError


@dc.dataclass
class Fix(Slippage):
    step: float

    def get_price(self, c: contract.Contract, o: trade.Order, price) -> float:
        return price + (self.step if o.order_num > 0 else -self.step)

    pass


@dc.dataclass
class Per(Slippage):
    rate: float

    def get_price(self, c: contract.Contract, o: trade.Order, price) -> float:
        return price * (1 + self.rate * (1 if o.order_num > 0 else -1))

    pass
