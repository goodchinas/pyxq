from dataclasses import dataclass

if __name__ == '__main__':
    pass


@dataclass
class Data(object):
    pass


@dataclass
class Order(Data):
    """
    fixme: OrderReq and OrderCancel is method,is not class.

    """
    pass


@dataclass
class Position(Data):
    pass


@dataclass
class Symbol(Data):
    """
    合约信息，名称、费率、
    """


@dataclass
class Account(Data):
    """
    采用保证金模式
    """
    name: str
    cash: float
    frozen: float

    @property
    def market(self):
        return None

    pass
