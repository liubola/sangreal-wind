import pandas as pd
import datetime as dt
from fastcache import lru_cache
from sangreal_wind.utils.engines import WIND_DB
from sangreal_wind.sangreal_calendar import adjust_trade_dt


@lru_cache()
def get_index_weight_all(index):
    index = '399300.SZ' if index == '000300.SH' else index
    table = getattr(WIND_DB, 'AIndexHS300FreeWeight'.upper())
    df = WIND_DB.query(
        table.S_CON_WINDCODE, table.I_WEIGHT,
        table.TRADE_DT).filter(table.S_INFO_WINDCODE == index).order_by(
            table.TRADE_DT.desc()).to_df()
    df.columns = ['sid', 'weight', 'trade_dt']
    df.weight = df.weight / 100.0
    return df


def get_index_weight(index, trade_dt=None):
    """[获取指数成份权重]
    
    Arguments:
        index {[str]} -- [windcode of index]
    
    Keyword Arguments:
        trade_dt {[str or datetime]} -- [trade_dt] (default: {None})
    
    Returns:
        [pd.DataFrame] -- [sid, weight]
    """

    if trade_dt is None:
        trade_dt = dt.date.today()
    trade_dt = adjust_trade_dt(trade_dt)
    df = get_index_weight_all(index).copy()
    df = df[(df['trade_dt'] <= trade_dt)]
    if df.empty:
        return pd.DataFrame()

    # 取出最近一个交易日
    t = df.trade_dt.iloc[0]
    df = df[df['trade_dt'] == t]
    df.drop(['trade_dt'], axis=1, inplace=True)
    return df.reset_index(drop=True)


if __name__ == '__main__':
    df = get_index_weight('000300.SH')
    print(df.head())
