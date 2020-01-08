import os
from itertools import chain

import pandas as pd
from sangreal_wind import WIND_DB


def china_td():
    """获取所有交易日
  
    Returns:
        list of 'trade_dt'
    """
    table = WIND_DB.ASHARECALENDAR
    df = WIND_DB.query(
        table.TRADE_DAYS).filter(table.S_INFO_EXCHMARKET == 'SSE').order_by(
            table.TRADE_DAYS).to_df()
    df.columns = ['trade_dt']
    return df.trade_dt.tolist()


def usa_td():
    pass


# 这个要作到说明文档中
dict_td = {
    'cn': china_td,
    'us': usa_td,
}


def mixin_trade_dt():
    country_list = os.environ.get('sangreal_calendar')
    if country_list is not None:
        country_list = country_list.split(',')
    else:
        country_list = [
            'cn',
        ]
    lst = list(set(chain(*(dict_td[k]() for k in country_list))))
    lst.sort()
    return pd.DataFrame(data=lst, columns=['trade_dt'])
