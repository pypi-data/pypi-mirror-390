# shivml/utils.py
import pandas as pd
from typing import Union

def load_data(data: Union[str, pd.DataFrame]):
    """Accept a CSV path or DataFrame. Return DataFrame."""
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, str):
        return pd.read_csv(data)
    raise ValueError("data must be a file path or pandas.DataFrame")
