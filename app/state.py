import json
import os

STATE_FILE = "data/state.json"

os.makedirs("data", exist_ok=True)


def load_state():

    if not os.path.exists(
        STATE_FILE
    ):
        return {}

    try:

        with open(
            STATE_FILE,
            "r"
        ) as f:

            content = f.read().strip()

            if not content:
                return {}

            return json.loads(content)

    except Exception:

        return {}


def save_state(state):

    with open(
        STATE_FILE,
        "w"
    ) as f:

        json.dump(
            state,
            f,
            indent=4
        )