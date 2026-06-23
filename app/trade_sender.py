import aiohttp

from app.logger import logger

FASTAPI_URL = "http://140.245.231.153:8000/signal"


async def send_trade_signal(
    previous_signal,
    signal,
    symbol,
    price
):

    payload = {

        "previous_signal":
        previous_signal,

        "signal":
        signal,

        "symbol":
        symbol,

        "price":
        price
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