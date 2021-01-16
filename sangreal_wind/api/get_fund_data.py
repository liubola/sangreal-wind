from collections import Iterable

from sangreal_wind.sangreal_calendar import CALENDAR
from sangreal_wind.utils.engines import WIND_DB
from sqlalchemy import func


def get_fund_nav(fund_list=None, begin_dt='20010101', end_dt='20990101'):
    """[获取基金净值]

    Keyword Arguments:
        fund_list {[str or iterable or None]} -- [list of funds or fund] (default: {None})
        begin_dt {str} -- [description] (default: {'20010101'})
        end_dt {str} -- [description] (default: {'20990101'})

    Returns:
        [pd.DataFrame] -- [f_sid|trade_dt|s_close]
    """

    table = WIND_DB.CHINAMUTUALFUNDNAV
    tmp_query = WIND_DB.query(table.F_INFO_WINDCODE, table.PRICE_DATE,
                              table.F_NAV_ADJFACTOR, table.F_NAV_UNIT).filter(
                                  table.PRICE_DATE >= begin_dt,
                                  table.PRICE_DATE <= end_dt).order_by(
                                      table.PRICE_DATE, table.F_INFO_WINDCODE)
    try:
        if isinstance(fund_list, str):
            tmp_query = tmp_query.filter(func.substring(
                table.F_INFO_WINDCODE, 1, 6) == fund_list[:6])
        elif isinstance(fund_list, Iterable):
            tmp_query = tmp_query.filter(func.substring(
                table.F_INFO_WINDCODE, 1, 6).in_([f[:6] for f in fund_list]))
        else:
            pass
    except:
        if isinstance(fund_list, str):
            tmp_query = tmp_query.filter(func.substr(
                table.F_INFO_WINDCODE, 1, 6) == fund_list[:6])
        elif isinstance(fund_list, Iterable):
            tmp_query = tmp_query.filter(func.substr(
                table.F_INFO_WINDCODE, 1, 6).in_([f[:6] for f in fund_list]))
        else:
            pass

    df = tmp_query.to_df()
    df.columns = ['f_sid', 'trade_dt', 'adjfactor', 'unit']
    df['s_close'] = df['adjfactor'] * df['unit']
    df.drop(['unit', 'adjfactor'], axis=1, inplace=True)
    trade_dt_list = CALENDAR.dates
    df = df[df.trade_dt.isin(trade_dt_list)].reset_index(drop=True)
    return df


if __name__ == '__main__':
    print(get_fund_nav('163407.OF'))
    # print(get_fund_nav(['000001.OF', '000002.OF']))
    # print(get_fund_nav(begin_dt='20190114'))
