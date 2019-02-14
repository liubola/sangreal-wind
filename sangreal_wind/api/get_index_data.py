import pandas as pd
from sangreal_wind.utils.engines import WIND_DB
from collections import Iterable


def get_index_data_tmp(index_list=None,
                       index_type='normal',
                       begin_dt='20010101',
                       end_dt='20990101'):
    """
    index_list 指数列表
    index_type 指数类型 1. 普通指数 2. 申万指数 3.中信指数
    """
    if index_type == 'normal':
        table = getattr(WIND_DB, 'AindexEODPrices'.upper())
    elif index_type == 'zx':
        table = getattr(WIND_DB, "AindexIndustriesEODCITICS".upper())
    elif index_type == "wind":
        table = getattr(WIND_DB, "AindexWindIndustriesEOD".upper())
    elif index_type == 'sw':
        table = getattr(WIND_DB, "ASWSIndexEOD".upper())

    tmp_query = WIND_DB.query(
        table.S_INFO_WINDCODE, table.TRADE_DT, table.S_DQ_OPEN,
        table.S_DQ_HIGH, table.S_DQ_LOW, table.S_DQ_CLOSE,
        table.S_DQ_VOLUME, table.S_DQ_AMOUNT).filter(
            table.TRADE_DT >= begin_dt, table.TRADE_DT <= end_dt).order_by(
                table.TRADE_DT, table.S_INFO_WINDCODE)
    if isinstance(index_list, str):
        tmp_query = tmp_query.filter(table.S_INFO_WINDCODE == index_list)
    elif isinstance(index_list, Iterable):
        tmp_query = tmp_query.filter(table.S_INFO_WINDCODE.in_(index_list))
    df = tmp_query.to_df()
    df.columns = [
        'sid', 'trade_dt', 's_open', 's_high', 's_low', 's_close', 's_volume',
        's_amount'
    ]
    return df


def get_index_data(index_list, begin_dt='20010101', end_dt='20990101'):
    """[获取指数数据 高开低收]
    
    Arguments:
        index_list {[str or list]} -- [windcode of index_list]
    
    Keyword Arguments:
        begin_dt {[str]} -- [description] (default: {'20010101'})
        end_dt {[str]} -- [description] (default: {'20990101'})
    
    Returns:
        [pd.DataFrame] -- ['sid', 'trade_dt', 's_open', 's_high', 's_low', 's_close', 's_volume', 's_amount']
    """

    if isinstance(index_list, str):
        index_list = {index_list}
    else:
        index_list = set(index_list)
    sw_list = set((i for i in index_list if i.endswith('SI')))
    zx_list = set((i for i in index_list if i.startswith('CI')))
    wind_list = set((i for i in index_list if i.startswith('88')))
    n_list = index_list - sw_list - zx_list - wind_list
    sw_df = get_index_data_tmp(
        index_list=sw_list, index_type='sw', begin_dt=begin_dt,
        end_dt=end_dt) if len(sw_list) > 0 else pd.DataFrame()
    wind_df = get_index_data_tmp(
        index_list=wind_list,
        index_type='wind',
        begin_dt=begin_dt,
        end_dt=end_dt) if len(wind_list) > 0 else pd.DataFrame()
    zx_df = get_index_data_tmp(
        index_list=zx_list, index_type='zx', begin_dt=begin_dt,
        end_dt=end_dt) if len(zx_list) > 0 else pd.DataFrame()
    n_df = get_index_data_tmp(
        index_list=n_list,
        index_type='normal',
        begin_dt=begin_dt,
        end_dt=end_dt) if len(n_list) > 0 else pd.DataFrame()
    df = pd.concat([wind_df, sw_df, zx_df, n_df],
                   axis=0,
                   ignore_index=True,
                   sort=False)
    return df


if __name__ == '__main__':
    print(get_index_data('000001.SH', ))
