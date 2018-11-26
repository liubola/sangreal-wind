import pandas as pd


def dt_handle(date):
    return pd.to_datetime(date).strftime('%Y%m%d')