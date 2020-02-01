"""
the father message type of other message type.
"""
import dataclasses as dc

from pyxq import ba


@dc.dataclass
class S(ba.Msg):
    s: str
