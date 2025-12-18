import pandas as pd
from energy_app.data.preprocess import fill_and_resample
from energy_app.data.windows import sliding_window


def test_resample_and_windowing():
    timestamps = pd.date_range("2024-01-01", periods=4, freq="2H", tz="UTC")
    df = pd.DataFrame({"timestamp": timestamps, "consumption": [1, 2, 3, 4]})
    resampled = fill_and_resample(df, freq="1H")
    assert len(resampled) == 7
    X, y = sliding_window(resampled["consumption"], window=3, horizon=2)
    assert X.shape[0] == len(resampled) - 3 - 2 + 1
    assert X.shape[1] == 3
    assert y.shape[1] == 2
