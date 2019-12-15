import dataclasses as dc
from unittest import TestCase
from datetime import datetime
import pyxq.base
from pyxq import cb as cb


@dc.dataclass
class ServerMsg(pyxq.base.Msg):
    text: str

    pass


@dc.dataclass
class ClientMsg(pyxq.base.Msg):
    text: str

    pass


class Server(object):
    def __init__(self, callback: cb.CallBack):
        self.callback = callback
        self.callback.bind(ClientMsg.key, self.show)
        pass

    def show(self, msg: ClientMsg):
        print(self.__class__.__name__, msg)

    def say(self, msg: str):
        self.callback.route(ServerMsg(dt=datetime.now(),text=msg))

    pass


class Client(object):
    def __init__(self, callback: cb.CallBack):
        self.callback = callback
        self.callback.bind(ServerMsg.key, self.show)
        pass

    def show(self, msg: ServerMsg):
        print(self.__class__.__name__, msg)

    def say(self, msg: str):
        self.callback.route(ClientMsg(dt=datetime.now(),text=msg))

    pass


class TestCallBack(TestCase):
    def test_callback(self):
        x = cb.CallBack()
        client = None
        server = None
        for i in range(3):
            client = Client(x)
            server = Server(x)
        client.say('hi,i am client!')
        server.say('hi,i am server!')

    pass


if __name__ == '__main__':
    pass
