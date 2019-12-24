from . import ba
from .msg import pa, md, td

"""
interface
"""


class IOrderRsp(ba.InterFace):
    def on_trade(self, x: td.Trade):
        raise NotImplementedError

    def on_ordered(self, x: td.Ordered):
        raise NotImplementedError

    def on_canceled(self, x: td.Canceled):
        raise NotImplementedError

    def on_rejected(self, x: td.Rejected):
        raise NotImplementedError


class IOrderReq(ba.InterFace):
    def on_order(self, x: td.OrderReq):
        raise NotImplementedError

    def on_cancel(self, x: td.Cancel):
        raise NotImplementedError


class IPaReq(ba.InterFace):
    def on_commission(self, x: pa.CommissionMsg):
        raise NotImplementedError

    def on_contract(self, x: pa.ContractMsg):
        raise NotImplementedError

    def on_cash(self, x: pa.Cash):
        raise NotImplementedError


class IMDRtn(ba.InterFace):
    def on_tick(self, x: md.Tick):
        raise NotImplementedError

    def on_order_book(self, x: md.OrderBook):
        raise NotImplementedError

    def on_open(self, x: md.Open):
        raise NotImplementedError

    def on_close(self, x: md.Close):
        raise NotImplementedError
