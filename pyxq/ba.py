import dataclasses as dc
from datetime import datetime

"""
the base of project class.
"""


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


_uid = 0


def uid():
    global _uid
    _uid += 1
    return _uid


@dc.dataclass
class Msg(object):
    """
    消息
    """
    key: int = dc.field(default=None, init=False, repr=False)
    id: str = dc.field(default_factory=lambda: str(uid()), init=False, repr=False)
    dt: datetime

    def __init_subclass__(cls, **kwargs):
        cls.key = hash(cls)


class Mod(object):
    """
    数据模型
    """
    pass


class Service(object):
    """
    服务
    """
    pass


class InterFace(object):
    """
    接口
    """
    pass
