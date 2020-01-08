import pandas as pd
from fastcache import lru_cache
from sangreal_wind.sangreal_calendar.datasource import mixin_trade_dt
from sangreal_wind.sangreal_calendar.utils import dt_handle


@lru_cache()
def get_all_trade_dt():
    """[获取所有交易日]
    
    Returns:
        [pd.DataFrame] -- [dataframe with columns of 'trade_dt']
    """

    # df = ts.trade_cal()
    # df = df[df['isOpen'] == 1][['calendarDate']]
    # df.columns = ['trade_dt']
    # df['trade_dt'] = df['trade_dt'].map(lambda x: x.replace('-', ''))
    return mixin_trade_dt()


def get_trade_dt_list(begin_dt='19900101', end_dt='20990101', astype='list'):
    """[获取指定时间段的所有交易日]
    
    Keyword Arguments:
        begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
        end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        astype {str} -- [list or pd] (default: {'list'})
    
    Raises:
        ValueError -- [f"astype:{astype} must be 'pd' or 'list'!"]
    
    Returns:
        [pd.DataFrame or list] -- [trade_dts between begin_dt and end_dt]
    """

    df = get_all_trade_dt()
    tmp_df = df.copy()
    begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
    tmp_df = tmp_df[(tmp_df['trade_dt'] >= begin_dt)
                    & (tmp_df['trade_dt'] <= end_dt)]
    if astype == 'pd':
        return tmp_df
    elif astype == 'list':
        return tmp_df['trade_dt'].tolist()
    else:
        raise ValueError(f"astype:{astype} must be 'pd' or 'list'!")
    """调整自然日至最近的交易日
    
    Args:
        date: date %Y%m%d or datetime.
        adjust: 'last' or 'next'.

    Returns:
        adjust type of trade_dt %Y%m%d
    """


@lru_cache()
def adjust_trade_dt(date, adjust='last'):
    """[adjust trade_dt]
    
    Arguments:
        date {[str or datetime]} -- [date]
    
    Keyword Arguments:
        adjust {str} -- [last or next] (default: {'last'})
    
    Raises:
        ValueError -- [f"adjust:{adjust} must be 'last' or 'next'!"]
    
    Returns:
        [str] -- [adjusted trade_dt with %Y%m%d type]
    """

    t_df = get_all_trade_dt()
    date = dt_handle(date)
    if adjust == 'last':
        t_df = t_df[t_df['trade_dt'] <= date]
        return t_df['trade_dt'].iloc[-1]
    elif adjust == 'next':
        t_df = t_df[t_df['trade_dt'] >= date]
        return t_df['trade_dt'].iloc[0]
    else:
        raise ValueError(f"adjust:{adjust} must be 'last' or 'next'!")


@lru_cache()
def step_trade_dt(date, step=1):
    """[step trade_dt]
    
    Arguments:
        date {[str or datetime]} -- [date]
    
    Keyword Arguments:
        step {int} -- [step] (default: {1})
    
    Returns:
        [str] -- [date with %Y%m%d type]
    """

    t_df = get_all_trade_dt()
    date = dt_handle(date)
    if step >= 0:
        try:
            return t_df[t_df['trade_dt'] >= date]['trade_dt'].iloc[step]
        except IndexError:
            return t_df['trade_dt'].iloc[-1]
    elif step < 0:
        try:
            return t_df[t_df['trade_dt'] < date]['trade_dt'].iloc[step]
        except IndexError:
            return t_df['trade_dt'].iloc[0]

@lru_cache()
def delta_trade_dt(begin_dt, end_dt):
    """[get length of trade_dt, include begin_dt and end_dt]
    
    Arguments:
        begin_dt {[str or datetime]} -- [begin_dt]
        end_dt {[tstr or datetime]} -- [end_dt]
    
    Returns:
        [int] -- [len of date_range]
    """

    t_df = get_all_trade_dt()
    begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
    return len(
        t_df[(t_df['trade_dt'] >= begin_dt) & (t_df['trade_dt'] <= end_dt)])


if __name__ == "__main__":
    import datetime as dt
    print(step_trade_dt('20180607', 1), '20180608')
    # 注意20171231为非交易日，自动视为20180102
    print(step_trade_dt('20171231', 1), '20180103')
    print(step_trade_dt('20171231', 1000), '20181231')
    print(step_trade_dt('20171231', -100000), '19901219')
    print(delta_trade_dt('20180102', '20180103'))
    print(get_trade_dt_list('20180101', dt.date.today()))
