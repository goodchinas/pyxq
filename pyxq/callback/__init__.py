from collections import defaultdict
import typing as t
from ..obj import event as e

EventType = t.TypeVar(name='EventType', bound=e.Event)
KeyType = t.TypeVar('KeyType', bound=int)
CallBackType = t.Callable[[EventType], None]


class CallBack(object):
    """
    manage the callbacks and event.
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
            raise ValueError('call back function is not in the X center.')

    def route(self, event: EventType):
        if event.key in self._callbacks:
            for cb in self._callbacks[event.key]:
                cb(event)