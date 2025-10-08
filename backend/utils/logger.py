import json
import time
from pathlib import Path
from .config import LOGS_DIR

def _ts():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def save_trace(trace: dict, filename: str = None):
    """
    Save a controller trace to logs directory.
    trace: dictionary with keys: input, decision, rationale, agents_called, documents, answer
    """
    if filename is None:
        filename = f"trace_{int(time.time())}.json"
    path = Path(LOGS_DIR) / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"ts": _ts(), **trace}, f, indent=2)
    return str(path)

def append_log(message: str, filename: str = "app.log"):
    path = Path(LOGS_DIR) / filename
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{_ts()}] {message}\n")
    return str(path)
