import itertools
from collections import namedtuple
from datetime import datetime

import numpy as np
import pandas as pd

from pyxq.msg import md, pa

s = [chr(_) for _ in range(ord('A'), ord("A") + 26)]  # the symbol list
contracts = [
    pa.Contract(num_per_unit=i, value_per_dot=j, margin_ratio=k)
    for i, j, k in [
        (100, 1, 1),
        (1, 300, .1),
        (.8, .8, .8),
    ]
]
contracts = (contracts * (len(s) // len(contracts) + 1))[:len(s)]
commissions = [
    pa.CommissionStockA(tax=i, commission=j, min_commission=k)
    for i, j, k in [
        (.001, .00025, 5),
        (.0005, .0005, 20),
    ]
]
commissions.extend([
    pa.CommissionFuture(rate=i)
    for i in [.1, 1, 10, 30]
])
commissions = (commissions * (len(s) // len(commissions) + 1))[:len(s)]
np.random.seed(8)  # the random seed
n = 2000 * 1  # days multiply numbers of one day.
prices = np.random.normal(loc=.0002, scale=0.02, size=(n, len(s)))
prices = np.exp(prices.cumsum(axis=0))
prices = np.around(prices * np.tile(np.random.randint(low=1, high=200, size=len(s)), reps=(n, 1)), decimals=2)
volumes = np.random.randint(low=1e4, high=1e5, size=(n, len(s))) * 100
dates = pd.date_range(start=datetime(year=2018, month=1, day=1), periods=n, freq='D')
is_new_day = list(itertools.chain([False], map(lambda x, y: x.date() != y.date(), dates[1:], dates[:-1])))
factors = np.random.normal(loc=.0, scale=0.01, size=(n, len(s)))

F = namedtuple(typename='F', field_names='x')


def get_msg():
    _msg = itertools.chain([itertools.chain(
        [pa.Cash(num=1e6, dt=dates[0])],
        map(lambda s, cm: pa.ContractNewMsg(s=s, dt=dates[0], cm=cm), s, contracts),
        map(lambda s, cm: pa.CommissionMsg(s=s, dt=dates[0], cm=cm), s, commissions),
    )])
    _rank = np.arange(len(s))
    np.random.seed(8)

    def _f(_date, _price, _volume, _new_day, _factor):
        _r = np.random.permutation(_rank)
        if _new_day:
            yield md.Close(dt=_date.date())
            # care that the factor data be made on no trade time.
            yield from map(lambda i: md.Factor(dt=_date, s=s[i], data=F(x=_factor[i])._asdict()), _r)
            yield md.Open(dt=_date.date())
        yield from map(lambda i: md.Tick(dt=_date, s=s[i], price=_price[i], volume=_volume[i]), _r)

    _msg = itertools.chain(
        _msg,
        map(
            lambda _date, _price, _volume, _new_day, _factor:
            _f(_date=_date, _price=_price, _volume=_volume, _new_day=_new_day, _factor=_factor),
            dates, prices, volumes, is_new_day, factors
        )
    )
    return _msg
