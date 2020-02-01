"""
trade message type.
"""
import dataclasses as dc

from .. import ba, cn


class ILS(ba.InterFace):
    @property
    def ls(self) -> cn.LS:
        """

        :return: cn.LS:operate the position type：long or short
        """

        raise NotImplementedError


@dc.dataclass
class OrderData(ba.Mod, ILS):
    s: str
    oc: cn.OC
    price: float
    num: float

    @property
    def ls(self) -> cn.LS:
        return (
            cn.LS.L if (self.num > 0 and self.oc == cn.OC.O) or (self.num < 0 and self.oc == cn.OC.C)
            else cn.LS.S)

    @property
    def bs(self) -> cn.BS:
        return cn.BS.B if self.num > 0 else cn.BS.S


@dc.dataclass
class Limit(OrderData):
    pass


@dc.dataclass
class Market(OrderData):
    """
    see：https://blog.csdn.net/u012724887/article/details/98502040
    """
    pass


@dc.dataclass
class OrderReq(ba.Msg):
    od: OrderData
    pass


@dc.dataclass
class OrderRsp(ba.Msg):
    orq: OrderReq


@dc.dataclass
class Ordered(OrderRsp):
    pass


@dc.dataclass
class Cancel(ba.Msg):
    ord: Ordered
    pass


@dc.dataclass
class Rejected(OrderRsp):
    pass


@dc.dataclass
class Canceled(OrderRsp):
    pass


@dc.dataclass
class Trade(OrderRsp, ILS):
    price: float
    num: float

    @property
    def ls(self) -> cn.LS:
        return cn.LS.L if (self.num > 0 and self.orq.od.oc == cn.OC.O) or \
                          (self.num < 0 and self.orq.od.oc == cn.OC.C) \
            else cn.LS.S

    pass
