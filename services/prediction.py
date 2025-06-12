import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from services.exchange_api import get_historical_rates_df

def forecast_rates_hw(
    source: str = "USD",
    currency: str = "EUR",
    history_days: int = 30,
    forecast_days: int = 7
) -> pd.DataFrame:
    """
    1) Fetch last `history_days` rates as a DataFrame
    2) Fit a Holt–Winters exponential smoothing model (additive trend)
    3) Forecast the next `forecast_days`
    4) Return a DataFrame with columns ['date','yhat','yhat_lower','yhat_upper']
       (we set lower=upper=yhat since this method doesn’t output CIs)
    """
    # 1) Pull the history
    df = get_historical_rates_df(
        source=source,
        currency=currency,
        days=history_days
    )

    # 2) Prepare series (date → index)
    df = df.set_index("date")
    series = df["rate"].astype(float)

    # 3) Fit Holt–Winters (additive trend, no seasonality)
    model = ExponentialSmoothing(series, trend="add", seasonal=None)
    fit = model.fit(optimized=True)

    # 4) Forecast out-of-sample
    fc = fit.forecast(forecast_days)

    # 5) Build result DataFrame
    df_fc = fc.reset_index()
    df_fc.columns = ["date", "yhat"]
    df_fc["yhat_lower"] = df_fc["yhat"]
    df_fc["yhat_upper"] = df_fc["yhat"]
    df_fc["date"] = df_fc["date"].dt.strftime("%Y-%m-%d")

    return df_fc
