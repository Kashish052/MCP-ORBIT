from __future__ import annotations
import json
import time
from pathlib import Path
from threading import RLock
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
STATE_FILE = DATA / "runtime_state.json"
LOG_FILE = DATA / "runtime_logs.jsonl"
INCIDENTS_FILE = DATA / "incidents.json"
AUDIT_FILE = DATA / "audit.jsonl"
LOCK = RLock()

DEFAULT_STATE = {
    "active_fault": None, "service": "orbit-demo-api", "error_rate": 0.01,
    "p95_latency_ms": 120, "database_pool_usage_pct": 35, "health": "healthy",
    "last_deployment": "deploy-2026-10-15-001", "recovery_count": 0,
}
MOCK_COMMITS = [
    {"sha":"a91c2ef","timestamp":"2026-10-15T09:42:00Z","author":"demo-engineer",
     "message":"Refactor configuration loader and environment validation",
     "files":["orbit_demo/config.py","orbit_demo/settings.py"],"risk_tags":["configuration","startup"]},
    {"sha":"b721a6d","timestamp":"2026-10-14T15:20:00Z","author":"demo-engineer",
     "message":"Optimize reporting query and add connection pooling",
     "files":["orbit_demo/repository.py"],"risk_tags":["database","performance"]},
    {"sha":"c8a0401","timestamp":"2026-10-13T11:10:00Z","author":"demo-engineer",
     "message":"Add request validation and error handling",
     "files":["orbit_demo/api.py"],"risk_tags":["api","validation"]},
]
def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")
def read_state() -> dict:
    with LOCK:
        if not STATE_FILE.exists(): _write_json(STATE_FILE, DEFAULT_STATE)
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
def write_state(value: dict) -> None:
    with LOCK: _write_json(STATE_FILE, value)
def append_log(level: str, message: str, **fields: Any) -> None:
    row = {"timestamp": time.time(), "level": level.upper(), "message": message, **fields}
    with LOCK:
        with LOG_FILE.open("a", encoding="utf-8") as f: f.write(json.dumps(row) + "\n")
def read_logs(limit: int = 100) -> list[dict]:
    if not LOG_FILE.exists(): return []
    with LOCK: lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    rows = []
    for line in lines[-max(1, min(limit, 500)):]:
        try: rows.append(json.loads(line))
        except json.JSONDecodeError: continue
    return rows
def load_json_list(path: Path) -> list[dict]:
    with LOCK:
        if not path.exists(): _write_json(path, [])
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            return value if isinstance(value, list) else []
        except json.JSONDecodeError: return []
def save_json_list(path: Path, value: list[dict]) -> None:
    with LOCK: _write_json(path, value)
def audit(event: str, actor: str = "system", details: dict | None = None) -> None:
    row = {"timestamp": time.time(), "event": event, "actor": actor, "details": details or {}}
    with LOCK:
        with AUDIT_FILE.open("a", encoding="utf-8") as f: f.write(json.dumps(row) + "\n")
def read_audit(limit: int = 100) -> list[dict]:
    if not AUDIT_FILE.exists(): return []
    with LOCK: lines = AUDIT_FILE.read_text(encoding="utf-8").splitlines()
    rows = []
    for line in lines[-max(1, min(limit, 500)):]:
        try: rows.append(json.loads(line))
        except json.JSONDecodeError: pass
    return list(reversed(rows))
