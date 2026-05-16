def generate_signal(df):

    # Closed candles only
    latest = df.iloc[-2]
    previous = df.iloc[-3]

    # =====================================
    # MAIN T3 DIRECTION
    # =====================================

    t3_main_green = (

        latest["t3_main"]
        > previous["t3_main"]
    )

    t3_main_red = (

        latest["t3_main"]
        < previous["t3_main"]
    )

    # =====================================
    # FIBO T3 DIRECTION
    # =====================================

    t3_fibo_green = (

        latest["t3_fibo"]
        > previous["t3_fibo"]
    )

    t3_fibo_red = (

        latest["t3_fibo"]
        < previous["t3_fibo"]
    )

    # =====================================
    # COMBINED TREND LOGIC
    # =====================================

    # BOTH GREEN = LONG
    if (
        t3_main_green
        and
        t3_fibo_green
    ):

        return "LONG"

    # BOTH RED = SHORT
    if (
        t3_main_red
        and
        t3_fibo_red
    ):

        return "SHORT"

    # MIXED COLORS = NEUTRAL
    return None