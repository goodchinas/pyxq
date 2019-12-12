import dataclasses as dc

from .. import base


@dc.dataclass
class Account(base.Msg):
    cash: float
    pass
