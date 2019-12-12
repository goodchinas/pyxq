import dataclasses as dc

import pyxq.base


@dc.dataclass
class Contract(pyxq.base.Msg):
    """
    抽象统一的保证金模式
    """
    symbol: str
    vol_per_unit: float
    value_per_dot: float
    margin_ratio: float

    def get_margin(self, value: float) -> float:
        return self.get_value(value) * self.margin_ratio

    def get_value(self, value: float):
        return value * self.value_per_dot

    pass
