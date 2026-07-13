import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def price_data():
    np.random.seed(99)
    symbols = [f"T{i}" for i in range(25)]
    n = 500
    data = {}
    for s in symbols:
        r = np.random.normal(0.0003, 0.016, n)
        data[s] = 100 * np.cumprod(1 + r)
    return pd.DataFrame(data, index=pd.bdate_range("2022-01-01", periods=n))


@pytest.fixture
def small_price_data():
    np.random.seed(7)
    n = 150
    data = {
        "AAPL": 100 * np.cumprod(1 + np.random.normal(0.0005, 0.02, n)),
        "MSFT": 100 * np.cumprod(1 + np.random.normal(0.0004, 0.018, n)),
        "GOOG": 100 * np.cumprod(1 + np.random.normal(0.0006, 0.022, n)),
    }
    return pd.DataFrame(data, index=pd.bdate_range("2023-06-01", periods=n))
