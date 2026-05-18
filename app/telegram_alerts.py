import aiohttp

from app.config import (
    BOT_TOKEN,
    CHAT_ID
)

from app.logger import logger


async def send_telegram_alert(message):

    try:

        logger.info(
            "Sending Telegram Alert..."
        )

        logger.info(
            f"BOT_TOKEN: {BOT_TOKEN}"
        )

        logger.info(
            f"CHAT_ID: {CHAT_ID}"
        )

        logger.info(
            f"MESSAGE: {message}"
        )

        url = (
            f"https://api.telegram.org/"
            f"bot{BOT_TOKEN}/sendMessage"
        )

        payload = {

            "chat_id":
            CHAT_ID,

            "text":
            message
        }

        async with aiohttp.ClientSession() as session:

            async with session.post(
                url,
                json=payload
            ) as response:

                result = await response.text()

                logger.info(
                    f"Telegram Response: {result}"
                )

                return result

    except Exception as e:

        logger.exception(
            f"Telegram Error: {e}"
        )

        return None