import aiohttp

from app.config import TIMEFRAME
from app.logger import logger
from datetime import datetime

FASTAPI_URL = "http://140.245.231.153:8000/signal"


async def send_trade_signal(
    signal,
    symbol,
    price
):

    payload = {

        "symbol": symbol,
        "signal": signal,
        "price": price,

        "qty": 1,

        "sl_points": 900,

        "tp_points": 50,
        "timeframe": TIMEFRAME.upper(),
    "timestamp": datetime.utcnow().isoformat()
    }

    try:

        async with aiohttp.ClientSession() as session:

            async with session.post(
                FASTAPI_URL,
                json=payload,
                timeout=10
            ) as response:

                result = await response.text()

                logger.info(
                    f"Trade Bot Response: {result}"
                )

                return result

    except Exception as e:

        logger.exception(
            f"Trade Signal Error: {e}"
        )

        return None