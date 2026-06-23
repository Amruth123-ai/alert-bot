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

from app.state import (
    load_state,
    save_state
)

from app.config import (
    SYMBOL,
    TIMEFRAME
)

from datetime import datetime

async def run_bot():

    logger.info("Bot Started")

    # =====================================
    # LOAD INITIAL CANDLES
    # =====================================

    df = await fetch_initial_candles()

    logger.info(
        f"Loaded {len(df)} candles"
    )

    # =====================================
    # CALCULATE CURRENT TREND
    # =====================================

    df = calculate_heikin_ashi(df)
    df = apply_indicators(df)

    current_signal = generate_signal(df)

    # =====================================
    # LOAD STATE
    # =====================================

    state = load_state()

    last_signal = state.get(
        "last_signal"
    )

    # =====================================
    # FIRST START ONLY
    # =====================================

    if last_signal is None:

        last_signal = current_signal

        state["last_signal"] = current_signal

        save_state(state)

        logger.info(
            f"Initial Signal Loaded: "
            f"{current_signal}"
        )

    else:

        logger.info(
            f"Previous Signal Loaded: "
            f"{last_signal}"
        )

    # =====================================
    # CONNECT WS
    # =====================================

    websocket = await connect_websocket()

    logger.info(
        "WebSocket connected"
    )

    while True:

        try:

            raw_message = (
                await websocket.recv()
            )

            data = json.loads(
                raw_message
            )

            # Ignore heartbeat
            if data.get("type") == "pong":
                continue

            # Ignore subscription response
            if data.get("type") == "subscriptions":
                continue

            # Process candle events only
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
                candle_data[
                    "candle_start_time"
                ]
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

            # Update current candle

            if (
                df.iloc[-1]["timestamp"]
                == candle["timestamp"]
            ):

                df.iloc[-1] = candle

            else:

                df = pd.concat([
                    df,
                    pd.DataFrame(
                        [candle]
                    )
                ]).reset_index(
                    drop=True
                )

                df = df.tail(200)

            # =====================================
            # APPLY INDICATORS
            # =====================================

            df = calculate_heikin_ashi(
                df
            )

            df = apply_indicators(
                df
            )

            signal = generate_signal(
                df
            )

            logger.info(
                f"Current Signal: "
                f"{signal}"
            )

            # =====================================
            # SIGNAL CHANGED
            # =====================================

            if signal != last_signal:

                logger.info(
                    f"Signal Changed: "
                    f"{last_signal}"
                    f" -> "
                    f"{signal}"
                )

                # =====================================
                # TELEGRAM MESSAGE
                # =====================================

                from datetime import datetime
                from zoneinfo import ZoneInfo

                alert_time = datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).strftime(
                    "%Y-%m-%d %H:%M:%S IST"
                )

                if signal == "LONG":

                    telegram_message = (
                        "🚀 LONG SIGNAL\n"
                    )

                elif signal == "SHORT":

                    telegram_message = (
                        "🔻 SHORT SIGNAL\n"
                    )

                else:

                    telegram_message = (
                        "⚪ NEUTRAL SIGNAL\n"
                    )

                telegram_message += (


                        f"Symbol: {SYMBOL}\n"

                        f"Price: "
                        f"{candle['close']}\n"

                        f"Alert Time: "
                        f"{alert_time}\n"

                        f"Current Trend: "
                        f"{signal}\n\n"

                        f"FROM ALERT-BOT"
                    )

                # =====================================
                # TELEGRAM ALERT
                # =====================================

                await send_telegram_alert(
                    telegram_message
                )

                # =====================================
                # FASTAPI TRADE BOT
                # =====================================

                await send_trade_signal(

                    previous_signal=
                    last_signal,

                    signal=
                    signal,

                    symbol=
                    SYMBOL,

                    price=
                    candle["close"]
                )

                logger.info(
                    "Telegram + Trade "
                    "Signal Sent"
                )

                # =====================================
                # SAVE STATE
                # =====================================

                last_signal = signal

                state[
                    "last_signal"
                ] = signal

                save_state(
                    state
                )

        except Exception as e:

            logger.exception(e)

            logger.info(
                "Reconnecting "
                "WebSocket..."
            )

            await asyncio.sleep(5)

            websocket = (
                await connect_websocket()
            )