from .. import ba, cb, actor
from ..service import account


class A0(ba.App):
    center: cb.CallBackManager
    a: account.Account

    def __init__(self, stg: actor.GateWay):
        a = account.Account()
        center = cb.CallBackManager()
        stg.init(a=a, center=center, broker=cb.CallBackManager())
        actor.Broker(
            a=a, center=center,
            gateway=stg.broker,
            exchange=actor.Exchange(center=center, broker=cb.CallBackManager()).broker)
        self.center = center
        self.a = a

    def route(self, x: ba.Msg):
        self.center.route(x=x)
