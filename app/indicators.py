def ema(series, length):

    return series.ewm(
        span=length,
        adjust=False
    ).mean()


def tillson_t3(
    source,
    length,
    vfactor
):

    # EMA chain
    e1 = ema(source, length)
    e2 = ema(e1, length)
    e3 = ema(e2, length)
    e4 = ema(e3, length)
    e5 = ema(e4, length)
    e6 = ema(e5, length)

    # Tillson coefficients
    c1 = -vfactor * vfactor * vfactor

    c2 = (
        3 * vfactor * vfactor
        + 3 * vfactor * vfactor * vfactor
    )

    c3 = (
        -6 * vfactor * vfactor
        - 3 * vfactor
        - 3 * vfactor * vfactor * vfactor
    )

    c4 = (
        1
        + 3 * vfactor
        + vfactor * vfactor * vfactor
        + 3 * vfactor * vfactor
    )

    # Final T3
    t3 = (
        c1 * e6
        + c2 * e5
        + c3 * e4
        + c4 * e3
    )

    return t3


def apply_indicators(df):

    # EXACT TradingView source:
    # (high + low + 2 * close) / 4

    source = (
        df["high"]
        + df["low"]
        + 2 * df["close"]
    ) / 4

    # Main T3
    df["t3_main"] = tillson_t3(

        source=source,

        length=8,

        vfactor=0.7
    )

    # Fibonacci T3
    df["t3_fibo"] = tillson_t3(

        source=source,

        length=5,

        vfactor=0.618
    )

    return df