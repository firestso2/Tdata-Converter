import os
from dataclasses import dataclass

FOOTER = "\n\n✍️ <i>Author: @vorache777</i>"

@dataclass
class Config:
    bot_token: str
    api_id: int
    api_hash: str
    device_model: str = "Samsung Galaxy S23"
    system_version: str = "Android 13"
    app_version: str = "10.3.2"
    lang_code: str = "en"
    system_lang_code: str = "en-US"

def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN"),
        api_id=int(os.getenv("API_ID", "2040")),
        api_hash=os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627"),
    )
