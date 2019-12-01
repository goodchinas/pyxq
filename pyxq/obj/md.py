from datetime import datetime

from pyxq.obj import Event


class Tick(Event):
    symbol: str

    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol

    pass


class Kline(Event):
    symbol: str
    dt: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __init__(self, symbol: str, dt: datetime, open: float, high: float, low: float, close: float, volume: float):
        super().__init__()
        self.symbol = symbol
        self.dt = dt
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    pass


class OrderBook(Event):
    symbol: str

    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol

    pass
