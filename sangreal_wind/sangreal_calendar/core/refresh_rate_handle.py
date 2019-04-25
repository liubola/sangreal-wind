from abc import ABCMeta, abstractmethod

import pandas as pd
from fastcache import lru_cache
from sangreal_wind.sangreal_calendar.core.trade_dt_handle import (
    adjust_trade_dt, get_trade_dt_list, step_trade_dt)
from sangreal_wind.sangreal_calendar.utils import dt_handle


class RefreshBase(metaclass=ABCMeta):
    """获取调仓日期的基类
    
    Attributes: 
        *args: -1 or 1, int or (1, -1)
    """

    def __init__(self, *args):
        if abs(sum(args)) > 1:
            raise ValueError('args must be 1 or -1')
        self.args = sorted(args, reverse=True)

    @abstractmethod
    def get(self, begin_dt, end_dt):
        pass

    @lru_cache()
    def next(self, date):
        """[get next date, 20180921 -> 20180928(Monthly(-1))]
        
        Arguments:
            date {[str or datetime]} -- [date]
        
        Returns:
            [str] -- [next day in class frequency]
        """

        end_dt = step_trade_dt(date, 300)
        df = self.get(date, end_dt).tolist()
        # if df[0] == date:
        #     return df[1]
        return df[0]

    @lru_cache()
    def prev(self, date):
        """[get previous day, 20180921 -> 20180831(Monthly(-1))]
        
        Arguments:
            date {[str or datetime]} -- [date]
        
        Returns:
            [str] -- [previous day in class frequency]
        """

        begin_dt = step_trade_dt(date, -300)
        df = self.get(begin_dt, date).tolist()
        # if df[-1] == date:
        #     return df[-2]
        return df[-1]

    @staticmethod
    def freq_handle(arg, df, step=1):
        if arg == 1:
            tmp_df = df['trade_dt'].apply(
                lambda x: adjust_trade_dt(x[:6] + '01', 'next'))
        elif arg == -1:
            tmp_df = df['trade_dt'].apply(
                lambda x: step_trade_dt(str(int(x[:6]) + step) + '01', -1))

        return tmp_df

    @staticmethod
    def df_handle(begin_dt='19900101', end_dt='20990101', func=None):
        begin_dt = dt_handle(begin_dt)
        end_dt = dt_handle(end_dt)
        df = get_trade_dt_list(begin_dt, end_dt, astype='pd').copy()

        df['trade_dt'] = df['trade_dt'].apply(func)
        df.drop_duplicates(inplace=True)
        return df

    def _get(self,
             begin_dt='19900101',
             end_dt='20990101',
             func=None,
             offset=None):
        begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
        df = get_trade_dt_list(
            step_trade_dt(begin_dt, -1 * offset),
            step_trade_dt(end_dt, offset),
            astype='pd').copy()
        df['_trade_dt'] = pd.to_datetime(df['trade_dt'])
        df['month'] = df['_trade_dt'].map(func)
        all_trade_dt = pd.Series()
        for arg in self.args:
            if arg == 1:
                tmp_df = df.drop_duplicates('month', keep='first')['trade_dt']
            elif arg == -1:
                tmp_df = df.drop_duplicates('month', keep='last')['trade_dt']
            all_trade_dt = pd.concat([all_trade_dt, tmp_df])
        all_trade_dt.sort_values(inplace=True)
        all_trade_dt = all_trade_dt[
            (all_trade_dt >= begin_dt)
            & (all_trade_dt <= end_dt)].drop_duplicates()
        return all_trade_dt


class Monthly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]
        
        Arguments:
            RefreshBase {[cls]} -- [refreshbase]
        
        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        
        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        def func(x):
            return f"{x.year}{x.month}"

        return self._get(
            begin_dt=begin_dt, end_dt=end_dt, func=func, offset=40)


class Weekly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]
        
        Arguments:
            RefreshBase {[cls]} -- [refreshbase]
        
        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        
        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        def func(x):
            return f"{x.year}{x.week}"

        return self._get(
            begin_dt=begin_dt, end_dt=end_dt, func=func, offset=20)


class BiWeekly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]
        
        Arguments:
            RefreshBase {[cls]} -- [refreshbase]
        
        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        
        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        all_trade_dt = pd.Series()
        for arg in self.args:
            if arg == 1:
                tmp_df = Weekly(1).get(begin_dt, end_dt)[::2]
            elif arg == -1:
                tmp_df = Weekly(-1).get(begin_dt, end_dt)[::2]
            all_trade_dt = pd.concat([all_trade_dt, tmp_df])
        all_trade_dt.sort_values(inplace=True)
        all_trade_dt.drop_duplicates(inplace=True)
        return all_trade_dt


class Quarterly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]
        
        Arguments:
            RefreshBase {[cls]} -- [refreshbase]
        
        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        
        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        def func(x):
            return f"{x.year}{x.quarter}"

        return self._get(
            begin_dt=begin_dt, end_dt=end_dt, func=func, offset=120)


class Reportly(RefreshBase):
    @staticmethod
    def _report(x):
        if x <= x[:4] + '0430':
            return str(int(x[:4]) - 1) + '11'
        elif x <= x[:4] + '0831':
            return x[:4] + '05'
        elif x <= x[:4] + '1031':
            return x[:4] + '09'
        elif x <= x[:4] + '1231':
            return x[:4] + '11'

    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]
        
        Arguments:
            RefreshBase {[cls]} -- [refreshbase]
        
        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        
        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
        df = self.df_handle(begin_dt, end_dt, self._report)
        all_trade_dt = pd.Series()
        for arg in self.args:
            if arg == 1:
                tmp_df = df['trade_dt'].apply(
                    lambda x: adjust_trade_dt(x[:6] + '01', 'next'))
            elif arg == -1:

                def neg_report(x):
                    if x[-2:] == '11':
                        return step_trade_dt(str(int(x[:4]) + 1) + '0501', -1)
                    elif x[-2:] == '09':
                        return step_trade_dt(x[:4] + '1101', -1)
                    elif x[-2:] == '05':
                        return step_trade_dt(x[:4] + '0901', -1)

                tmp_df = df['trade_dt'].apply(neg_report)
            all_trade_dt = pd.concat([all_trade_dt, tmp_df])
        all_trade_dt.sort_values(inplace=True)
        # all_trade_dt = pd.to_datetime(all_trade_dt)
        return all_trade_dt[(all_trade_dt >= begin_dt)
                            & (all_trade_dt <= end_dt)]


class Yearly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]
        
        Arguments:
            RefreshBase {[cls]} -- [refreshbase]
        
        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        
        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        def func(x):
            return f"{x.year}"

        return self._get(
            begin_dt=begin_dt, end_dt=end_dt, func=func, offset=300)


class Halfyearly(RefreshBase):
    @staticmethod
    def _year(x):
        if x <= x[:4] + '0630':
            return x[:4] + '01'
        elif x <= x[:4] + '1231':
            return x[:4] + '07'

    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]
        
        Arguments:
            RefreshBase {[cls]} -- [refreshbase]
        
        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        
        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
        df = self.df_handle(begin_dt, end_dt, self._year)
        all_trade_dt = pd.Series()
        for arg in self.args:
            tmp_df = self.freq_handle(arg, df, 6)
            all_trade_dt = pd.concat([all_trade_dt, tmp_df])
        all_trade_dt.sort_values(inplace=True)
        return all_trade_dt[(all_trade_dt >= begin_dt)
                            & (all_trade_dt <= end_dt)]


if __name__ == '__main__':
    m = Halfyearly(-1)
    lst = m.get()
    print(lst, type(lst))
    print(m.next('20161220'), m.prev('20161220'))
