import os
from importlib import import_module
from typing import cast
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from math import log10, floor

from .influx import Influx
from .time import Time


def divide(x, y):
    if isinstance(y, (np.ndarray, pd.Series)):
        y_safe = y.copy()
        y_safe[y_safe == 0] = np.nan
    else:
        y_safe = np.nan if y == 0 else y

    return x / y_safe


def getconf(conf_name, variable):
    conf_module_path = os.getenv("CONF_MODULE_PATH")
    module_path = f"{conf_module_path}.{conf_name}"
    conf_module = import_module(module_path)
    return getattr(conf_module, variable)


def filter_df(df: pd.DataFrame, col: str, range: list) -> pd.DataFrame:
    filtered_df = df[(df[col] > range[0]) & (df[col] < range[1])]
    return cast(pd.DataFrame, filtered_df.reset_index(drop=True))


def get_unique_values(series: pd.Series, tol: float) -> np.typing.NDArray:
    rounded = (series / tol).round() * tol
    return rounded.unique()


def apply_sig_figs(x: float, n: int = 3) -> float:
    if x == 0 or np.isnan(x):
        return x
    rounded = round(x, -int(floor(log10(abs(x)))) + (n - 1))
    if rounded == int(rounded):
        return int(rounded)
    return rounded


def apply_sig_figs_to_df(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    float_cols = df.select_dtypes(include=["float64", "float32"]).columns
    df.loc[:, float_cols] = df[float_cols].map(lambda x: apply_sig_figs(x, n))
    return df
