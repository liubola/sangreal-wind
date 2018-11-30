import re
from fastcache import lru_cache
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from sangreal_wind.utils import dt_handle

from sangreal_wind.utils.engines import WIND_DB


def get_industry(trade_dt, sid=None, level=1):
    """[get industry of stock 中信行业]
    
    Arguments:
        trade_dt {[str or datetime]} -- [trade_dt]
    
    Keyword Arguments:
        sid {[str or iterable]} -- [sids of stocks] (default: {None})
        level {int} -- [level of zx industry] (default: {1})
    
    Returns:
        [pd.DataFrame] -- [sid: ind]
    """

    trade_dt = dt_handle(trade_dt)
    df = get_industry_all(level)
    if sid is not None:
        sid = {sid} if isinstance(sid, str) else set(sid)
        df = df[df['sid'].isin(sid)]

    df = df.loc[(df['entry_dt'] <= trade_dt) & (
        (df['out_dt'] >= trade_dt) | (df['out_dt'].isnull()))].copy()
    return df.set_index('sid')[['ind']]


@lru_cache()
def get_industry_all(level=1):
    clss = WIND_DB.ASHAREINDUSTRIESCLASSCITICS
    ind_code = WIND_DB.ASHAREINDUSTRIESCODE
    df = WIND_DB.query(
        clss.S_INFO_WINDCODE, clss.ENTRY_DT, clss.REMOVE_DT,
        ind_code.INDUSTRIESNAME).filter(ind_code.LEVELNUM == (level + 1))
    try:
        df = df.filter(
            func.substring(clss.CITICS_IND_CODE, 1, 2 + 2 * level) == func.
            substring(ind_code.INDUSTRIESCODE, 1, 2 + 2 * level)).to_df()
    except OperationalError:
        df = df.filter(
            func.substr(clss.CITICS_IND_CODE, 1, 2 + 2 * level) == func.substr(
                ind_code.INDUSTRIESCODE, 1, 2 + 2 * level)).to_df()
    df.columns = ['sid', 'entry_dt', 'out_dt', 'ind']
    return df


def get_industry_sp(trade_dt, sid=None, split=['银行', '非银行金融']):
    """[将split中部分中信一级行业转换为相应的二级行业]
    
    Arguments:
        trade_dt {[str]} -- [description]
    
    Keyword Arguments:
        sid      {[str or iterable]} -- [sids of stocks] (default: {None})
        split      {list} -- [industry which convert level1 to level2] (default: {['银行', '非银行金融']})
    
    Returns:
        [pd.DataFrame] -- [sid: ind]
    """
    trade_dt = dt_handle(trade_dt)
    df = get_industry_all(level=1)
    if sid is not None:
        sid = {sid} if isinstance(sid, str) else set(sid)
        df = df[df['sid'].isin(sid)]

    df = df.loc[(df['entry_dt'] <= trade_dt) & (
        (df['out_dt'] >= trade_dt) | (df['out_dt'].isnull()))].copy()

    split_sid = df[df['ind'].isin(split)]
    normal_sid = df[~(df['ind'].isin(split))]
    df1 = get_industry_all(level=2)
    df1 = df1[df1['sid'].isin(split_sid.sid)]

    df1 = df1.loc[(df1['entry_dt'] <= trade_dt) & (
        (df1['out_dt'] >= trade_dt) | (df1['out_dt'].isnull()))].copy()
    # 将一级和二级合并
    df = normal_sid.append(df1, ignore_index=True)

    # 去除行业中的罗马数字
    p = re.compile(r"[^\u4e00-\u9fa5]")
    df.ind = df.ind.str.replace(p, '', regex=True)
    return df.set_index('sid')[['ind']]


if __name__ == '__main__':
    print(get_industry('20181122').head())
