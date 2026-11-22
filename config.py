import os
from dotenv  import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN","")

def _parse_ids(raw_value:str | None) -> list[int]:
    if not raw_value:
        return []
    return [int(item.strip()) for item in raw_value.split(",") if item.strip()]

ADMIN_ID : list[int] = _parse_ids(os.getenv("ADMIN_ID"))
BARISTA_ID: list[int] = _parse_ids(os.getenv("BARISTA_ID"))

