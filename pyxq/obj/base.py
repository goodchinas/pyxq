import uuid


class Model(object):
    """
    所有事件参数的基类
    """
    pass


class Event(object):
    """
    所有事件数据对象的父类
    """

    def __init__(self):
        self._key = self.cls_key()
        self.id = str(uuid.uuid1())

    @classmethod
    def cls_key(cls) -> int:
        return hash(cls)

    @property
    def key(self) -> int:
        return self._key
