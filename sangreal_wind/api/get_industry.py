import re
from functools import lru_cache
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from sangreal_wind.utils import dt_handle

from sangreal_wind.utils.engines import WIND_DB


class DynamicIndustry:
    def __init__(self, ind=None):
        self.ind = ind

    def preview(self, trade_dt, adjust=True):
        # adjust {bool} -- [由于中信变更行业分类，是否调整兼容之前的代码] (default: {True})
        all_stk = get_industry(trade_dt=trade_dt, level=1, sid=None, adjust=adjust)
        if self.ind is not None:
            return set(all_stk[all_stk['ind'] == self.ind].index)
        return set(all_stk.index)


def get_industry(trade_dt, sid=None, level=1, adjust=True):
    """[get industry of stock 中信行业]

    Arguments:
        trade_dt {[str or datetime]} -- [trade_dt]

    Keyword Arguments:
        sid {[str or iterable]} -- [sids of stocks] (default: {None})
        level {int} -- [level of zx industry] (default: {1})
        adjust {bool} -- [由于中信变更行业分类，是否调整兼容之前的代码] (default: {True})

    Returns:
        [pd.DataFrame] -- [sid: ind]
    """

    trade_dt = dt_handle(trade_dt)
    df = get_industry_all(level=level, adjust=adjust)
    if sid is not None:
        sid = {sid} if isinstance(sid, str) else set(sid)
        df = df[df['sid'].isin(sid)]

    df = df.loc[(df['entry_dt'] <= trade_dt) & (
        (df['out_dt'] >= trade_dt) | (df['out_dt'].isnull()))].copy()
    return df.set_index('sid')[['ind']]


@lru_cache()
def get_industry_all(level=1, adjust=True):
    """[summary]
    adjust {bool} -- [由于中信变更行业分类，是否调整兼容之前的代码] (default: {True})
    """
    clss = WIND_DB.ASHAREINDUSTRIESCLASSCITICS
    ind_code = WIND_DB.ASHAREINDUSTRIESCODE
    df = WIND_DB.query(
        clss.S_INFO_WINDCODE, clss.ENTRY_DT, clss.REMOVE_DT,
        ind_code.INDUSTRIESNAME).filter(ind_code.LEVELNUM == (level + 1))
    try:
        df = df.filter(
            func.substring(clss.CITICS_IND_CODE, 1, 2 + 2 * level) == func.
            substring(ind_code.INDUSTRIESCODE, 1, 2 + 2 * level)).to_df()
    except:
        df = df.filter(
            func.substr(clss.CITICS_IND_CODE, 1, 2 + 2 * level) == func.substr(
                ind_code.INDUSTRIESCODE, 1, 2 + 2 * level)).to_df()
    df.columns = ['sid', 'entry_dt', 'out_dt', 'ind']
    # 去除行业中的罗马数字
    p = re.compile(r"[^\u4e00-\u9fa5]")
    df.ind = df.ind.str.replace(p, '', regex=True)
    # 将综合金融放入非银行金融内
    if adjust:
        def ind_map(x):
            if x == '综合金融':
                return '非银行金融'
            elif x in ('多领域控股', '资产管理', '新兴金融服务'):
                return '多元金融'
            elif x in ('全国性股份制银行', '区域性银行'):
                return '股份制与城商行'
            else:
                return x
        df.ind = df.ind.map(ind_map)
    return df


def get_industry_sp(trade_dt, sid=None, split=['银行', '非银行金融', '综合金融'], adjust=True):
    """[将split中部分中信一级行业转换为相应的二级行业]

    Arguments:
        trade_dt {[str]} -- [description]

    Keyword Arguments:
        sid      {[str or iterable]} -- [sids of stocks] (default: {None})
        split      {list} -- [industry which convert level1 to level2] (default: {['银行', '非银行金融']})
        adjust {bool} -- [由于中信变更行业分类，是否调整兼容之前的代码] (default: {True})

    Returns:
        [pd.DataFrame] -- [sid: ind]
    """
    trade_dt = dt_handle(trade_dt)
    df = get_industry_all(level=1, adjust=adjust)
    if sid is not None:
        sid = {sid} if isinstance(sid, str) else set(sid)
        df = df[df['sid'].isin(sid)]

    df = df.loc[(df['entry_dt'] <= trade_dt) & (
        (df['out_dt'] >= trade_dt) | (df['out_dt'].isnull()))].copy()

    split_sid = df[df['ind'].isin(split)]
    normal_sid = df[~(df['ind'].isin(split))]
    df1 = get_industry_all(level=2, adjust=adjust)
    df1 = df1[df1['sid'].isin(split_sid.sid)]

    df1 = df1.loc[(df1['entry_dt'] <= trade_dt) & (
        (df1['out_dt'] >= trade_dt) | (df1['out_dt'].isnull()))].copy()
    # 将一级和二级合并
    df = normal_sid.append(df1, ignore_index=True)

    return df.set_index('sid')[['ind']]


if __name__ == '__main__':
    print(len(DynamicIndustry().preview('20180101')))
