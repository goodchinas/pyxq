import dataclasses as dc
import typing as tp

import pyxq.base
import pyxq.msg
from pyxq import const as ct
from pyxq.msg import contract, trade, commission
from pyxq.msg.trade import Trade, Rejected, Canceled


@dc.dataclass
class Position(tp.Deque[pyxq.msg.trade.Trade]):
    contract: contract.Contract
    price: float
    frozen: float = dc.field(init=False, default=0)

    def close(self, x: pyxq.msg.trade.Trade) -> float:
        self.frozen -= x.volume
        _volume = x.volume  # 剩余成交量
        _profit = 0  # 平仓盈亏
        _t = None  # 当前待平历史持仓
        while _volume > 0:
            if abs(self[0].volume) > abs(_volume):
                _t = self[0]
                _t.volume -= _volume
                _profit += self.contract.get_value(value=_volume * (x.price - _t.price))
                _volume = 0
            else:
                _t = self.popleft()
                _profit += self.contract.get_value(value=_t.volume * (x.price - _t.price))
                _volume -= _t.volume
        return _profit

    @property
    def profit(self) -> float:
        return self.contract.get_value(
            value=
            sum([t.volume for t in self]) * self.price -
            sum([t.volume * t.price for t in self])
        )

    @property
    def margin(self) -> float:
        return self.contract.get_margin(value=abs(sum([t.volume for t in self])) * self.price)


class IOrderRsp(object):
    def trade(self, x: Trade):
        raise NotImplementedError

    def rejected(self, x: Rejected):
        raise NotImplementedError

    def canceled(self, x: Canceled):
        raise NotImplementedError

    pass


@dc.dataclass
class Order(tp.List[Trade], IOrderRsp):
    order: trade.Order

    def trade(self, x: Trade) -> None:
        self.order.trade_num += x.volume
        # return self.ordering

    def rejected(self, x: Rejected) -> None:
        self.order.reject_nm += x.num

    def canceled(self, x: Canceled):
        self.order.cancel_nm += x.num

    def commission(self, x: commission.Commission, y: contract.Contract) -> float:
        return x.get(y, self)
        pass

    def frozen(self, x: contract.Contract) -> float:
        return x.get_margin(
            value=(
                      abs(self.order.order_num) -
                      abs(self.order.trade_num + self.order.cancel_nm + self.order.reject_nm)) * self.order.price
        )

    @property
    def ordering(self):
        return self.order.order_num - (self.order.trade_num + self.order.cancel_nm + self.order.reject_nm)

    pass


class Account(pyxq.base.Msg, IOrderRsp):
    """
    持仓、权益、处理成交
    # todo 更新行情，另起一个事件
        监控信息流，记录委托成交等信息
    """
    cash: float
    orders: tp.Dict[str, Order]  # 维护订单、手续费
    positions: tp.DefaultDict[float, tp.Dict[str, Position]]
    commissions: tp.Dict[str, commission.Commission]
    contracts: tp.Dict[str, contract.Contract]

    @property
    def margin(self) -> float:
        return sum([p.margin for i in self.positions.values() for p in i.values()])

    @property
    def profit(self) -> float:
        return sum([p.profit for i in self.positions.values() for p in i.values()])

    @property
    def frozen(self):
        return sum([i.frozen(self.contracts[i.order.symbol]) for i in self.orders.values()])

    @property
    def equity(self) -> float:
        return self.margin + self.cash + self.frozen

    def order_req(self, o: trade.Order):
        self.orders[o.id] = o

    def trade(self, x: pyxq.msg.trade.Trade):
        if x.symbol not in self.positions[x.bs]:
            self.positions[x.bs][x.symbol] = Position(contract=self.contracts[x.symbol], price=x.price)
        _position = self.positions[x.bs][x.symbol]
        if x.oc == ct.OC.O:
            _position.append(x)
        else:
            _position.close(x=x)
            if len(_position) == 0:
                del self.positions[x.bs][x.symbol]
        self.orders[x.order_id].trade(x)
        self.order_rsp(x.order_id)

    def canceled(self, x: pyxq.msg.trade.Canceled):
        self.orders[x.order_id].canceled(x)
        self.order_rsp(x.order_id)

    def rejected(self, x: pyxq.msg.trade.Rejected):
        self.orders[x.order_id].rejected(x)
        self.order_rsp(x.order_id)

    def order_rsp(self, x: str):
        if self.orders[x].ordering == 0:
            del self.orders[x]

    pass
