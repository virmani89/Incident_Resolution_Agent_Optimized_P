from configparser import ConfigParser
from pathlib import Path

CONFIG_FILE = Path(__file__).with_name("uiconfigfile.ini")
_config = ConfigParser()
_config.read(CONFIG_FILE, encoding="utf-8")

class Config:
    PAGE_TITLE = _config.get("DEFAULT", "PAGE_TITLE", fallback="Agentic Incident Resolution Assistant")
    PAGE_ICON = _config.get("DEFAULT", "PAGE_ICON", fallback="🔎")
    LAYOUT = _config.get("DEFAULT", "LAYOUT", fallback="wide")
