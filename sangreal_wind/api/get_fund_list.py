from sangreal_wind.utils.engines import WIND_DB
from sangreal_wind.utils.fund_type import FUND_TYPE
from fastcache import lru_cache
from collections import Iterable

FUND_TYPE_LEVEL0 = ['股票型基金', '混合型基金', '债券型基金']


@lru_cache()
def get_fund_list():
    table0 = getattr(WIND_DB, 'ChinaMutualFundSector'.upper())
    table1 = getattr(WIND_DB, 'AShareIndustriesCode'.upper())
    df = WIND_DB.query(table0.F_INFO_WINDCODE, table0.S_INFO_SECTORENTRYDT,
                       table0.S_INFO_SECTOREXITDT,
                       table1.INDUSTRIESNAME).filter(
                           table0.S_INFO_SECTOR == table1.INDUSTRIESCODE,
                           table0.S_INFO_SECTORENTRYDT != None,
                           table0.S_INFO_SECTOREXITDT == None).to_df()
    df.columns = [c.lower() for c in df.columns]
    df = df[df['INDUSTRIESNAME'.lower()].isin(FUND_TYPE)]
    df.columns = ['sid', 'entry_dt', 'exit_dt', 'fund_type']
    return df


def get_fund_filter(fundtype='all'):
    """[选取同一类型下的基金]
    
    Keyword Arguments:
        fundtype {str} -- [基金类型] (default: {'all'})
    
    Raises:
        ValueError -- [description]
    
    Returns:
        [pd.Series] -- [Series of fund]
    """

    df = get_fund_list()
    if fundtype == 'all':
        return df.sid
    elif fundtype == '股票型':
        return df[df['fund_type'].isin((
            '普通股票型基金',
            '被动指数型基金',
            '增强指数型基金',
        ))].sid
    elif fundtype == '混合型':
        return df[df['fund_type'].isin((
            '偏股混合型基金',
            '平衡混合型基金',
            '偏债混合型基金',
            '灵活配置型基金',
        ))].sid
    elif fundtype == '债券型':
        return df[df['fund_type'].isin((
            '中长期纯债型基金',
            '短期纯债型基金',
            '混合债券型一级基金',
            '混合债券型二级基金',
            '被动指数型债券基金',
            '增强指数型债券基金',
        ))].sid
    elif isinstance(fundtype, str):
        tmp_f = fundtype.rstrip('基金') + '基金'
        return df[df['fund_type'] == tmp_f].sid
    elif isinstance(fundtype, Iterable):
        tmp_fundtype = [f.rstrip('基金') + '基金' for f in fundtype]
        return df[df['fund_type'].isin(tmp_fundtype)].sid
    else:
        raise ValueError(f'请输入正确的基金类型！ 如{FUND_TYPE_LEVEL0 + FUND_TYPE}')


if __name__ == '__main__':
    print(get_fund_filter('all').head())
    print(get_fund_filter('债券型').head())
    print(get_fund_filter('中长期纯债型基').head())
    print(get_fund_filter(['中长期纯债型基', '中长期纯债型基']).head())
