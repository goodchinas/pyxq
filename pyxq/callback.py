import typing as t
from collections import defaultdict

import pyxq.obj

KeyType = t.TypeVar(name='KeyType', bound=int)
EventType = t.TypeVar(name='EventType', bound=pyxq.obj.base.Event)
CallBackType = t.Callable[[], None]


class CallBack(object):
    """
    manage the callbacks and obj.
    """
    _callbacks: t.Dict[KeyType, t.List[CallBackType]]

    def __init__(self):
        self._callbacks = defaultdict(list)
        pass

    def bind(self, key: KeyType, callback: CallBackType):
        call_back_list = self._callbacks[key]
        if callback not in call_back_list:
            call_back_list.append(callback)
        else:
            raise ValueError('call back function only be promised register once.')

    def unbind(self, key: KeyType, callback: CallBackType):
        call_back_list = self._callbacks[key]
        if callback in call_back_list:
            call_back_list.remove(callback)
        else:
            raise ValueError('call back function is not in the manage center.')

    def route(self, event: EventType):
        if event.key in self._callbacks:
            for cb in self._callbacks[event.key]:
                cb(event)
