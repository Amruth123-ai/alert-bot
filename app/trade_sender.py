import aiohttp

from app.logger import logger

FASTAPI_URL = "http://140.245.231.153:8000/webhook"


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

        "tp_points": 50
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