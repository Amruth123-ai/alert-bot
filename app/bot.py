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

from app.trade_sender import (
    send_trade_signal
)

from app.config import (
    SYMBOL,
    TIMEFRAME
)


async def run_bot():

    logger.info("Bot Started")

    df = await fetch_initial_candles()

    logger.info(
        f"Loaded {len(df)} candles"
    )

    last_signal = None

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

            # ignore heartbeat
            if data.get("type") == "pong":
                continue

            # ignore subscriptions
            if data.get("type") == "subscriptions":
                continue

            # process candle messages only
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

            candle_timestamp = int(
                candle_data["candle_start_time"]
            )

            candle_timestamp = (
                candle_timestamp // 1_000_000
            )

            candle = {

                "timestamp":
                pd.to_datetime(
                    candle_timestamp,
                    unit="s",
                    utc=True
                ),

                "open":
                float(candle_data["open"]),

                "high":
                float(candle_data["high"]),

                "low":
                float(candle_data["low"]),

                "close":
                float(candle_data["close"]),

                "volume":
                float(candle_data["volume"])
            }

            # update current candle
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

            # indicators
            df = calculate_heikin_ashi(df)

            df = apply_indicators(df)

            signal = generate_signal(df)

            logger.info(
                f"Generated Signal: {signal}"
            )

            # signal changed
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
                    f"Timeframe: {TIMEFRAME.upper()}\n"
                    f"Price: {candle['close']}\n"
                    f"Trend: {signal} T3"
                )

                # Telegram Alert
                await send_telegram_alert(
                    telegram_message
                )

                # FastAPI Trade Bot
                await send_trade_signal(
                    signal=signal,
                    symbol=SYMBOL,
                    price=candle["close"]
                )

                logger.info(
                    f"Telegram + Trade Signal Sent: {signal}"
                )

                last_signal = signal

        except Exception as e:

            logger.exception(e)

            logger.info(
                "Reconnecting WebSocket..."
            )

            await asyncio.sleep(5)

            websocket = (
                await connect_websocket()
            )