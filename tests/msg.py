import itertools
from collections import namedtuple
from datetime import datetime

import numpy as np
import pandas as pd

from pyxq.msg import md, pa

F = namedtuple(typename='F', field_names='x')


def _get_data():
    # simulate data
    np.random.seed(8)  # the random seed
    _n = 2000 * 1  # days multiply numbers of one day.
    _s = [chr(_) for _ in range(ord('A'), ord("A") + 26)]  # the symbol list
    _prices = np.random.normal(loc=.0002, scale=0.02, size=(_n, len(_s)))
    _prices = np.exp(_prices.cumsum(axis=0))
    _prices = np.around(_prices * np.tile(np.random.randint(low=1, high=200, size=len(_s)), reps=(_n, 1)), decimals=2)
    _volumes = np.random.randint(low=1e4, high=1e5, size=(_n, len(_s))) * 100
    _dates = pd.date_range(start=datetime(year=2018, month=1, day=1), periods=_n, freq='D')
    _is_new_day = list(itertools.chain([False], map(lambda x, y: x.date() != y.date(), _dates[1:], _dates[:-1])))
    _factors = np.random.normal(loc=.0, scale=0.01, size=(_n, len(_s)))
    return _s, _prices, _volumes, _dates, _is_new_day, _factors


S, _prices, _volumes, _dates, _is_new_day, _factors = _get_data()
_contracts = [
    pa.Contract(num_per_unit=i, value_per_dot=j, margin_ratio=k)
    for i, j, k in [
        (12.34, 5.6, .5)
        # (100, 1, 1),
        # (1, 300, .1),
        # (.8, .8, .8),
    ]
]
_contracts = (_contracts * (len(S) // len(_contracts) + 1))[:len(S)]

_commissions = [
    pa.CommissionStockA(tax=i, commission=j, min_commission=k)
    for i, j, k in [
        (.001, .00025, 5),
        # (.0005, .0005, 20),
    ]
]
# _commissions.extend([
#     pa.CommissionFuture(rate=i)
#     for i in [.1, 1, 10, 30]
# ])
_commissions = (_commissions * (len(S) // len(_commissions) + 1))[:len(S)]


def get_msg():
    _msg = itertools.chain([itertools.chain(
        [pa.Cash(num=1e6, dt=_dates[0])],
        map(lambda s, cm: pa.ContractNewMsg(s=s, dt=_dates[0], cm=cm), S, _contracts),
        map(lambda s, cm: pa.CommissionMsg(s=s, dt=_dates[0], cm=cm), S, _commissions),
    )])
    _rank = np.arange(len(S))
    np.random.seed(8)

    def _f(_date, _price, _volume, _new_day, _factor):
        _r = np.random.permutation(_rank)
        if _new_day:
            yield md.Close(dt=_date.date())
            # care that the factor data be made on no trade time.
            yield from map(lambda i: md.Factor(dt=_date, s=S[i], data=F(x=_factor[i])._asdict()), _r)
            yield md.Open(dt=_date.date())
        yield from map(lambda i: md.Tick(dt=_date, s=S[i], price=_price[i], volume=_volume[i]), _r)

    _msg = itertools.chain(
        _msg,
        map(
            lambda _date, _price, _volume, _new_day, _factor:
            _f(_date=_date, _price=_price, _volume=_volume, _new_day=_new_day, _factor=_factor),
            _dates, _prices, _volumes, _is_new_day, _factors
        )
    )
    return _msg
