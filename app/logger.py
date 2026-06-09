import logging
import sys
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s - "
        "%(levelname)s - "
        "%(message)s"
    ),

    handlers=[

        logging.StreamHandler(
            sys.stdout
        ),

        logging.FileHandler(
            "logs/bot.log"
        )
    ]
)

logger = logging.getLogger(
    "delta_ws_bot"
)
#