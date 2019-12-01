from unittest import TestCase

import pyxq.callback
import pyxq.obj
import pyxq.obj.base
from pyxq import callback as cb


class ServerMsg(pyxq.obj.base.Event):
    text: str

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    pass


class ClientMsg(pyxq.obj.base.Event):
    text: str

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    pass


class Server(object):
    def __init__(self, callback: pyxq.callback.CallBack):
        self.callback = callback
        self.callback.bind(ClientMsg.cls_key(), self.show)
        pass

    def show(self, msg: ClientMsg):
        print(self, msg)

    def say(self, msg: str):
        self.callback.route(ServerMsg(msg))

    pass


class Client(object):
    def __init__(self, callback: pyxq.callback.CallBack):
        self.callback = callback
        self.callback.bind(ServerMsg.cls_key(), self.show)
        pass

    def show(self, msg: ServerMsg):
        print(self, msg)

    def say(self, msg: str):
        self.callback.route(ClientMsg(msg))

    pass


class TestCallBack(TestCase):
    def test_callback(self):
        x = pyxq.callback.CallBack()
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
