import dataclasses as dc
from .. import ba

"""
the message base type.
"""


@dc.dataclass
class Symbol(ba.Msg):
    symbol: str
