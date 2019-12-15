import dataclasses as dc
import uuid
from datetime import datetime


class Actor(object):
    """
    角色
    """
    pass


class App(object):
    """
    应用：模拟交易
    """
    pass


@dc.dataclass
class Msg(object):
    """
    消息
    """
    key: int = dc.field(default=None, init=False, repr=False)
    id: str = dc.field(default_factory=lambda: str(uuid.uuid1()), init=False, repr=False)
    dt: datetime

    def __init_subclass__(cls, **kwargs):
        cls.key = hash(cls)


class Service(object):
    """
    服务
    """
    pass
