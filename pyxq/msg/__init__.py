import dataclasses as dc
from .. import ba

"""
the message base type.
"""


@dc.dataclass
class S(ba.Msg):
    s: str
