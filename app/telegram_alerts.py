import aiohttp

from app.config import (
    BOT_TOKEN,
    CHAT_ID
)

from app.logger import logger


async def send_telegram_alert(message):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": message
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