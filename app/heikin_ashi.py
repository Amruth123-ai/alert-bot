import pandas as pd


def calculate_heikin_ashi(df):

    ha_df = df.copy()

    ha_close = (
        df["open"] +
        df["high"] +
        df["low"] +
        df["close"]
    ) / 4

    ha_open = [
        (
            df["open"].iloc[0]
            + df["close"].iloc[0]
        ) / 2
    ]

    for i in range(1, len(df)):

        ha_open.append(
            (
                ha_open[i - 1]
                + ha_close.iloc[i - 1]
            ) / 2
        )

    ha_df["ha_open"] = ha_open
    ha_df["ha_close"] = ha_close

    ha_df["ha_high"] = ha_df[
        ["high", "ha_open", "ha_close"]
    ].max(axis=1)

    ha_df["ha_low"] = ha_df[
        ["low", "ha_open", "ha_close"]
    ].min(axis=1)

    return ha_df