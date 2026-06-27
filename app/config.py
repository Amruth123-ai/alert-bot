from dotenv import load_dotenv
import os

load_dotenv()

DELTA_REST_URL = os.getenv("DELTA_REST_URL")
DELTA_WS_URL = os.getenv("DELTA_WS_URL")

SYMBOL = os.getenv("SYMBOL", "BTCUSD")
TIMEFRAME = os.getenv("TIMEFRAME", "5m")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PRICE_BUFFER = 99