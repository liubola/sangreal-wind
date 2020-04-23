import os
import pandas as pd


def dt_handle(date):
    try:
        return pd.to_datetime(date).strftime('%Y%m%d')
    except ValueError:
        return date


def set(country=None):
    """
    country: list or iterable
    """
    if country is not None:
        if isinstance(country, str):
            country = [
                country,
            ]
        os.environ['sangreal_calendar'] = ','.join(country)