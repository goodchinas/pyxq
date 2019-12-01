from . import base
import typing as t
from . import order


class AccountModel(base.Model):
    """
    持仓、权益、处理成交
    """
    orders: t.Dict[str, order.OrderModel]
    positions: dict
    trades: dict
    pass


class AccountEvent(base.Event):
    pass
