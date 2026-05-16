import asyncio
import json
import pandas as pd

from app.logger import logger

from app.delta_rest import (
    fetch_initial_candles
)

from app.websocket_client import (
    connect_websocket
)

from app.heikin_ashi import (
    calculate_heikin_ashi
)

from app.indicators import (
    apply_indicators
)

from app.signals import (
    generate_signal
)

from app.telegram_alerts import (
    send_telegram_alert
)

from app.state import (
    load_state,
    save_state
)

from app.config import (
    SYMBOL,
    TIMEFRAME
)


async def run_bot():

    logger.info("Bot Started")

    # initial candles
    df = await fetch_initial_candles()

    logger.info(
        f"Loaded {len(df)} candles"
    )

    # state load
    state = load_state()

    # create state if missing
    if not state:

        save_state({
            "last_signal": None,
            "last_alert_timestamp": None
        })

        state = load_state()

    last_signal = state.get(
        "last_signal"
    )

    last_alert_timestamp = state.get(
        "last_alert_timestamp"
    )

    websocket = await connect_websocket()

    logger.info(
        "WebSocket connected"
    )

    while True:

        try:

            raw_message = await websocket.recv()

            data = json.loads(
                raw_message
            )

            logger.info(data)

            # ignore heartbeat
            if data.get("type") == "pong":
                continue

            # ignore subscriptions
            if data.get("type") == "subscriptions":
                continue

            # detect candle message
            if (
                "candle"
                not in str(data).lower()
            ):
                continue

            candle_data = (
                data.get("payload")
                or data.get("data")
                or data
            )

            if not candle_data:
                continue

            # candle parsing
            # candle parsing
            # delta websocket uses microseconds

            candle_timestamp = int(
                candle_data["candle_start_time"]
            )

            # convert microseconds → seconds
            candle_timestamp = (
                candle_timestamp // 1_000_000
            )

            # candle parsing
            candle = {

                "timestamp":
                pd.to_datetime(
                    candle_timestamp,
                    unit="s",
                    utc=True
                ),

                "open":
                float(
                    candle_data["open"]
                ),

                "high":
                float(
                    candle_data["high"]
                ),

                "low":
                float(
                    candle_data["low"]
                ),

                "close":
                float(
                    candle_data["close"]
                ),

                "volume":
                float(
                    candle_data["volume"]
                )
            }

            # update or append candle
            if (
                df.iloc[-1]["timestamp"]
                == candle["timestamp"]
            ):

                df.iloc[-1] = candle

            else:

                df = pd.concat([
                    df,
                    pd.DataFrame([candle])
                ]).reset_index(drop=True)

                df = df.tail(200)

            # process only once per candle
            current_timestamp = (
            int(
                candle_data[
                    "candle_start_time"
                ]
            ) // 1_000_000
        )

            if (
                last_alert_timestamp
                == current_timestamp
            ):
                continue

            # indicators
            df = calculate_heikin_ashi(df)

            df = apply_indicators(df)

            signal = generate_signal(df)

            logger.info(
                f"Generated Signal: {signal}"
            )

            # send signal
            if (
                signal
                and signal != last_signal
            ):

                telegram_message = (

                    "🚀 LONG SIGNAL\n"

                    if signal == "LONG"

                    else

                    "🔻 SHORT SIGNAL\n"
                )

                telegram_message += (

                    f"Symbol: {SYMBOL}\n"

                    f"Timeframe: "
                    f"{TIMEFRAME.upper()}\n"

                    f"Price: "
                    f"{candle['close']}\n"

                    f"Trend: "
                    f"{signal} T3"
                )

                await send_telegram_alert(
                    telegram_message
                )

                logger.info(
                    f"Signal Sent: {signal}"
                )

                last_signal = signal

                last_alert_timestamp = (
                    current_timestamp
                )

                save_state({

                    "last_signal":
                    last_signal,

                    "last_alert_timestamp":
                    last_alert_timestamp
                })

        except Exception as e:

            logger.exception(e)

            logger.info(
                "Reconnecting WebSocket..."
            )

            await asyncio.sleep(5)

            websocket = (
                await connect_websocket()
            )