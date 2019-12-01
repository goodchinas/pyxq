from pyxq.obj import Event


class Cancel(Event):
    symbol: str

    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol

    pass
