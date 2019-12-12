import dataclasses as dc
import typing as tp

import pyxq.base
from . import contract, trade


@dc.dataclass
class Commission(pyxq.base.Msg):
    symbol: str

    def get(self, c: contract.Contract, ts: tp.List[trade.Trade]):
        raise NotImplementedError

    pass


class Fix(Commission):
    every: float

    def get(self, c: contract.Contract, ts: tp.List[trade.Trade]) -> float:
        return sum((t.volume for t in ts)) * self.every

    pass


class Per(Commission):
    rate: float

    def get(self, c: contract.Contract, ts: tp.List[trade.Trade]) -> float:
        return sum([t.volume * t.price * c.value_per_dot for t in ts]) * self.rate

    pass
