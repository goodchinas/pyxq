import typing as t
from collections import defaultdict
import uuid
from . import ba

CallBackType = t.Callable[[], None]
"""
the callback center.
"""


class CallBackManager(object):
    """
    manage the callbacks and msg.
    """
    id: str
    _callbacks: t.Dict[int, t.List[CallBackType]]

    def __init__(self):
        self.id = str(uuid.uuid1())
        self._callbacks = defaultdict(list)
        pass

    def bind(self, key: int, callback: CallBackType):
        call_back_list = self._callbacks[key]
        if callback not in call_back_list:
            call_back_list.append(callback)
        else:
            raise ValueError('call back function only be promised register once.')

    def unbind(self, key: int, callback: CallBackType):
        call_back_list = self._callbacks[key]
        if callback in call_back_list:
            call_back_list.remove(callback)
        else:
            raise ValueError('call back function is not in the manage center.')

    def route(self, x: ba.Msg):
        [cb(x) for k, v in self._callbacks.items() if k == x.key for cb in v]
