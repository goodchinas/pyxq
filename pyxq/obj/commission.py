import pyxq.obj.order
from . import base
from . import trade


class CommissionModel(base.Model):
    def calculate(self, o: pyxq.obj.order.OrderEvent):
        raise NotImplementedError
        pass

    pass


class CommissionStock(CommissionModel):
    def __init__(self):
        pass

    def calculate(self, o: pyxq.obj.order.OrderEvent) -> float:
        return 0.0

    pass


class CommissionFuture(CommissionModel):
    def __init__(self):
        pass

    def calculate(self, o: pyxq.obj.order.OrderEvent) -> float:
        return 0.0

    pass


class CommissionEvent(base.Event):
    symbol: str
    commission: CommissionModel

    def __init__(self, s: str, c: CommissionModel):
        super().__init__()
        self.symbol = s
        self.commission = c

    pass
