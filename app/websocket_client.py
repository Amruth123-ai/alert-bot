import json
import websockets

from app.config import (
    DELTA_WS_URL,
    SYMBOL,
    TIMEFRAME
)


async def connect_websocket():

    websocket = await websockets.connect(

        DELTA_WS_URL,

        ping_interval=15,
        ping_timeout=30,

        close_timeout=10,

        max_queue=None,

        compression=None
    )

    subscribe_payload = {
        "type": "subscribe",
        "payload": {
            "channels": [
                {
                    "name":
                    f"candlestick_{TIMEFRAME}",

                    "symbols": [SYMBOL]
                }
            ]
        }
    }

    await websocket.send(
        json.dumps(subscribe_payload)
    )

    return websocket