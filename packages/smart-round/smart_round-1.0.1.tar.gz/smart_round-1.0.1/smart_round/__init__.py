try:
    import numpy as np
except ImportError:
    np = None
try:
    import pandas as pd
except ImportError:
    pd = None


def smart_round(i: float, tail: int=2) -> float:
    if i == 0:
        return 0.0
    if abs(i) >= 1:
        return round(i, tail)
    c_tail = 0
    while round(i, c_tail) == 0:
        c_tail += 1
    return round(i, max(tail, c_tail))


def format_value(val: float, tail=3) -> str:
    if np is None:
        raise ImportError('Install NumPy module with `pip install numpy`')
    if np.isnan(val):
        return ''
    rt = np.format_float_positional(smart_round(val, tail))
    if rt.endswith('.'):
        rt = rt+'0'
    return rt


def format_dataframe(df: pd.DataFrame, tail=3) -> pd.DataFrame:
    if pd is None:
        raise ImportError('Install pandas module with `pip install pandas`')
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].apply(lambda x: format_value(x, tail))
    return df