import dataclasses as dc

from .. import base


@dc.dataclass
class Symbol(base.Msg):
    symbol: str
