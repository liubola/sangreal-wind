from fastcache import lru_cache
from sangreal_calendar import adjust_trade_dt
from sqlalchemy import func
from sqlalchemy.exc import OperationalError

from ..utils.engines import WIND_DB


def get_industry(trade_dt, sid=None, level=1):
    """返回trade_dt时间截面上对应sid的中信行业分类.

    Args:
        trade_dt: str or datetime.
        sid: str or tuple.
        level: level of zx industry.
        
    Returns:
        DataFrame like |sid|trade_dt(datetime)|ind_sid|ind_name|
    """
    df = get_industry_all(level)
    if sid is not None:
        sid = {sid} if isinstance(sid, str) else set(sid)
        df = df[df['sid'].isin(sid)]

    df = df.loc[(df['entry_dt'] <= trade_dt) & (
        (df['out_dt'] >= trade_dt) | (df['out_dt'].isnull()))].copy()
    df['trade_dt'] = adjust_trade_dt(trade_dt)
    return df[[
        'sid',
        'trade_dt',
        'ind_name',
    ]]


@lru_cache()
def get_industry_all(level=1):
    clss = WIND_DB.ASHAREINDUSTRIESCLASSCITICS
    ind_code = WIND_DB.ASHAREINDUSTRIESCODE
    df = WIND_DB.query(
        clss.S_INFO_WINDCODE, clss.ENTRY_DT, clss.REMOVE_DT,
        ind_code.INDUSTRIESNAME).filter(ind_code.LEVELNUM == (level + 1))
    try:
        df = df.filter(
            func.substring(clss.CITICS_IND_CODE, 1, 4) == func.substring(
                ind_code.INDUSTRIESCODE, 1, 4)).to_df()
    except OperationalError:
        df = df.filter(
            func.substr(clss.CITICS_IND_CODE, 1, 2 + 2 * level) == func.substr(
                ind_code.INDUSTRIESCODE, 1, 2 + 2 * level)).to_df()
    df.columns = ['sid', 'entry_dt', 'out_dt', 'ind_name']
    return df


if __name__ == '__main__':
    print(get_industry_all().head())
