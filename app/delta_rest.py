import aiohttp
import pandas as pd

from datetime import (
    datetime,
    timedelta,
    timezone
)

from app.config import (
    DELTA_REST_URL,
    SYMBOL,
    TIMEFRAME
)


async def fetch_initial_candles(limit=100):

    end_time = datetime.now(
        timezone.utc
    )

    tf_minutes = int(
        TIMEFRAME.replace("m", "")
    )

    start_time = (
        end_time
        - timedelta(
            minutes=tf_minutes * limit
        )
    )

    url = (
        f"{DELTA_REST_URL}"
        f"/v2/history/candles"
    )

    params = {
        "symbol": SYMBOL,
        "resolution": TIMEFRAME,
        "start": int(
            start_time.timestamp()
        ),
        "end": int(
            end_time.timestamp()
        )
    }

    async with aiohttp.ClientSession() as session:

        async with session.get(
            url,
            params=params
        ) as response:

            data = await response.json()

            if not data.get("success"):

                raise Exception(
                    f"Delta REST Error: {data}"
                )

            candles = data["result"]

            df = pd.DataFrame(candles)

            df = df.rename(columns={
                "time": "timestamp"
            })

            df["timestamp"] = pd.to_datetime(
                df["timestamp"],
                unit="s",
                utc=True
            )

            numeric_cols = [
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]

            for col in numeric_cols:

                df[col] = pd.to_numeric(
                    df[col]
                )

            return (
                df.sort_values(
                    "timestamp"
                ).reset_index(drop=True)
            )