from sangreal_wind.utils.engines import WIND_DB
from sangreal_wind.utils.datetime_handle import dt_handle
from sangreal_calendar import step_trade_dt


def get_daily_ret(
        sid=None,
        trade_dt=None,
        begin_dt='20030101',
        end_dt='20990101',
):
    """[get daily_ret of stocks,]
    
    Keyword Arguments:
        sid {[sid or iterable]} -- [stock windcode] (default: {None})
        begin_dt {str or datetime} -- [begin_dt] (default: {'20030101'})
        end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        trade_dt {[str or datetime]} -- [trade_dt] (default: {None})

    Returns:
        ret {pd.DataFrame} -- [sid: trade_dt]
    """
    begin_dt, end_dt = step_trade_dt(dt_handle(begin_dt),
                                     -1), dt_handle(end_dt)
    table = getattr(WIND_DB, 'AShareEODPrices'.upper())
    query = WIND_DB.query(table.S_INFO_WINDCODE, table.TRADE_DT,
                          table.S_DQ_ADJCLOSE)
    if sid is not None:
        if isinstance(sid, str):
            query = query.filter(table.S_INFO_WINDCODE == sid)
        else:
            query = query.filter(table.S_INFO_WINDCODE.in_(sid))

    if trade_dt is not None:
        begin_dt = step_trade_dt(trade_dt, -1)
        end_dt = dt_handle(trade_dt)
    df = query.filter(table.TRADE_DT >= begin_dt,
                      table.TRADE_DT <= end_dt).order_by(
                          table.TRADE_DT).to_df()
    df.columns = ['sid', 'trade_dt', 'close']
    df = df.pivot(values='close', index='trade_dt', columns='sid')
    df = df.pct_change(fill_method=None)
    df.dropna(how='all', inplace=True)
    return df.T


if __name__ == '__main__':
    df = get_daily_ret(begin_dt='20181101')
    print(df)
