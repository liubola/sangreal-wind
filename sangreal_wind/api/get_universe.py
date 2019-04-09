import attr
import pandas as pd
from fastcache import lru_cache
from sangreal_wind.utils.commons import INDEX_DICT
from sangreal_wind.utils.datetime_handle import dt_handle
from sangreal_wind.utils.engines import WIND_DB

indx_error = f"请输入正确的指数简称，如{list(INDEX_DICT.keys())}，或指数wind代码！"


def universe_A(cur_sign=True):
    """[返回最新全A成份股]

    Keyword Arguments:
        cur_sign {bool} -- [是否需要最新的股票池] (default: {True})

    Returns:
        [set] -- [set of stk code]
    """

    table = WIND_DB.AINDEXMEMBERSWIND
    query = WIND_DB.query(table.S_CON_WINDCODE).filter(
        table.F_INFO_WINDCODE == '881001.WI')
    if cur_sign:
        df = query.filter(table.CUR_SIGN == '1').to_df()
    else:
        df = query.to_df()
    df.columns = ['sid']
    return set(df.sid)


def universe_normal(indx, cur_sign=True):
    """[返回指数的最新份股]

    Arguments:
        indx {[str]} -- [wind code of index]
        cur_sign {bool} -- [是否需要最新的股票池] (default: {True})
    Raises:
        ValueError -- [description]
        ValueError -- [description]

    Returns:
        [set] -- [set of stk code]
    """

    try:
        indx = INDEX_DICT[indx]
    except KeyError:
        if '.' not in indx:
            raise ValueError(indx_error)
    table = getattr(WIND_DB, 'AIndexMembers'.upper())
    query = WIND_DB.query(table.S_CON_WINDCODE).filter(
        table.S_INFO_WINDCODE == indx)
    if cur_sign:
        df = query.filter(
            table.CUR_SIGN == '1', ).to_df()
    else:
        df = query.to_df()
    df.columns = ['sid']
    if df.empty:
        raise ValueError(indx_error)
    return set(df.sid)


def universe_msci(cur_sign=True):
    """[返回MSCI最新成分股]
    Arguments:
        cur_sign {bool} -- [是否需要最新的股票池] (default: {True})

    Returns:
        [set] -- [set of stk code]
    """

    table = getattr(WIND_DB, 'AshareMSCIMembers'.upper())
    query = WIND_DB.query(
        table.S_INFO_WINDCODE)
    if cur_sign:
        df = query.filter(table.CUR_SIGN == '1').to_df()
    else:
        df = query.to_df()

    df.columns = ['sid']
    return set(df.sid)


def Universe(indx, cur_sign=True):
    """[返回指数的最新成分股]

    Arguments:
        indx {[str]} -- [wind code of index or abbrev]
        cur_sign {bool} -- [是否需要最新的股票池] (default: {True})

    Returns:
        [set] -- [set of stk code]
    """

    if indx == 'MSCI':
        return universe_msci(cur_sign=cur_sign)
    elif indx == 'A':
        return universe_A(cur_sign=cur_sign)
    else:
        return universe_normal(indx, cur_sign=cur_sign)


@lru_cache()
def get_all_normal_index(index):
    table = getattr(WIND_DB, 'AIndexMembers'.upper())
    df = WIND_DB.query(
        table.S_CON_WINDCODE, table.S_CON_INDATE,
        table.S_CON_OUTDATE).filter(table.S_INFO_WINDCODE == index).to_df()
    df.columns = ['sid', 'entry_dt', 'out_dt']
    return df


@lru_cache()
def get_all_msci():
    table = getattr(WIND_DB, 'AshareMSCIMembers'.upper())
    df = WIND_DB.query(table.S_INFO_WINDCODE,
                       table.ENTRY_DT, table.REMOVE_DT).to_df()
    df.columns = ['sid', 'entry_dt', 'out_dt']
    return df


@lru_cache()
def get_all_stk():
    table = getattr(WIND_DB, 'AIndexMembersWind'.upper())
    df = WIND_DB.query(table.S_CON_WINDCODE, table.S_CON_INDATE,
                       table.S_CON_OUTDATE).filter(
                           table.F_INFO_WINDCODE == '881001.WI').to_df()

    df.columns = ['sid', 'entry_dt', 'out_dt']
    return df


@attr.s
class DynamicUniverse:
    """[get stock_list of universe on trade_dt]

    Raises:
        ValueError -- [description]

    Returns:
        [set] -- [description]
    """

    indx = attr.ib()
    index = attr.ib(init=False)

    @indx.validator
    def check(self, attribute, value):
        if value not in INDEX_DICT.keys():
            if '.' not in value:
                raise ValueError(indx_error)

    def __attrs_post_init__(self):
        try:
            self.index = INDEX_DICT[self.indx]
        except KeyError:
            self.index = self.indx

    def preview(self, trade_dt):
        if self.index != '':
            df = get_all_normal_index(self.index)
        elif self.indx == 'MSCI':
            df = get_all_msci()
        elif self.indx == 'A':
            df = get_all_stk()

        trade_dt = dt_handle(trade_dt)
        df = df.loc[(df['entry_dt'] <= trade_dt) & (
            (df['out_dt'] >= trade_dt) | (df['out_dt'].isnull()))]
        return set(df.sid)


if __name__ == '__main__':
    f_list = DynamicUniverse('HS300').preview('20180105')
    print(len(f_list))
