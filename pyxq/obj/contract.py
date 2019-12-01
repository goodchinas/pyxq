from pyxq.obj import base


class ContractModel(base.Model):
    symbol: str
    volume_per_unit: float
    value_per_dot: float
    pass


class ContractEvent(base.Event):
    cm: ContractModel

    def __init__(self, cm: ContractModel):
        super().__init__()
        self.cm = cm
