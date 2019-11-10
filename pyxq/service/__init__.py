from typing import Any


class DataCenter(object):
    """
    数据接收、存储和读取中心。数据缓存用，维护缓存窗口
    """

    def get_x(self):
        """
        获取数据
        :return:
        """
        pass

    def on_x(self):
        """
        监听存储数据
        :return:
        """
        pass

    pass


class GateWay(object):
    """
    中间网关/代理服务：对接行情和交易
    fixme 属于策略等继承的父类
    """

    def on_x(self, data: Any):
        """
        回调类方法
        :param data:
        :return:
        """
        pass

    def re_x(self, data: Any):
        """
        请求类方法
        :param data:
        :return:
        """
        pass

    pass


class Broker(object):
    """
    账户维护：网关/代理右侧，模拟类服务。
    订单、仓位、资产和绩效分析
    存储仓位，不需要存储委托和成交（缓存都数据中心一份）
    todo **账户服务，多账户数据**
    """
    positions: dict

    pass


class Simulation(object):
    """
    模拟交易所，网关/代理右侧，行情和订单撮合
    """
    pass
