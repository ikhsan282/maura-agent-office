#!/usr/bin/env python3
"""Maura Agent Office — stdlib-only live dashboard server."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sqlite3
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DEFAULT_DBS = [
    Path.home() / ".hermes/kanban.db",
    Path.home() / ".hermes/kanban/boards/deskrpg-fe7b484593fa486999a823325d8d79d4/kanban.db",
]
AGENTS = [
    {"id": "default", "name": "Bos", "role": "Orchestrator", "brand": "Maura Group", "emoji": "👑", "desk": "command"},
    {"id": "maura-trans-internal", "name": "Trans Internal", "role": "Operasional & SEO", "brand": "Maura Trans", "emoji": "🚐", "desk": "trans"},
    {"id": "maura-trans-cs", "name": "Trans CS", "role": "Customer Service", "brand": "Maura Trans", "emoji": "💬", "desk": "trans-cs"},
    {"id": "maura-printing-internal", "name": "Printing Internal", "role": "Produk & SEO", "brand": "Maura Printing", "emoji": "🖨️", "desk": "print"},
    {"id": "maura-printing-cs", "name": "Printing CS", "role": "Customer Service", "brand": "Maura Printing", "emoji": "🎧", "desk": "print-cs"},
]


def _task_rows(db_path: Path) -> list[dict]:
    if not db_path.exists():
        return []
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=1)
        con.row_factory = sqlite3.Row
        columns = {r[1] for r in con.execute("PRAGMA table_info(tasks)")}
        needed = {"id", "title", "assignee", "status"}
        if not needed <= columns:
            con.close()
            return []
        optional = [c for c in ("priority", "created_at", "started_at", "completed_at") if c in columns]
        selected = ["id", "title", "assignee", "status", *optional]
        rows = [dict(r) for r in con.execute(f"SELECT {','.join(selected)} FROM tasks")]
        con.close()
        return rows
    except (sqlite3.Error, OSError):
        return []


def collect_state(db_paths: list[Path] | None = None, now: float | None = None) -> dict:
    now = now or time.time()
    tasks: dict[str, dict] = {}
    for db in db_paths or DEFAULT_DBS:
        for task in _task_rows(Path(db)):
            previous = tasks.get(task["id"])
            stamp = max(task.get("completed_at") or 0, task.get("started_at") or 0, task.get("created_at") or 0)
            old_stamp = max((previous or {}).get("completed_at") or 0, (previous or {}).get("started_at") or 0, (previous or {}).get("created_at") or 0)
            if previous is None or stamp >= old_stamp:
                tasks[task["id"]] = task

    by_agent: dict[str, list[dict]] = {}
    for task in tasks.values():
        by_agent.setdefault(task.get("assignee") or "", []).append(task)

    agents = []
    for definition in AGENTS:
        assigned = by_agent.get(definition["id"], [])
        running = sorted(
            (t for t in assigned if t.get("status") in {"running", "review"}),
            key=lambda t: (t.get("priority") or 0, t.get("started_at") or 0),
            reverse=True,
        )
        recent = sorted(
            (t for t in assigned if t.get("status") == "done" and (t.get("completed_at") or 0) > now - 3600),
            key=lambda t: t.get("completed_at") or 0,
            reverse=True,
        )
        current = (running or recent or [None])[0]
        status = "working" if running else "recent" if recent else "idle"
        agents.append({**definition, "status": status, "task": current, "assigned": len(assigned)})

    ready = sum(t.get("status") in {"ready", "todo"} for t in tasks.values())
    working = sum(a["status"] == "working" for a in agents)
    done_today = sum(t.get("status") == "done" and (t.get("completed_at") or 0) > now - 86400 for t in tasks.values())
    try:
        load1, _, _ = os.getloadavg()
    except OSError:
        load1 = 0.0
    mem_total = mem_free = 0
    try:
        values = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            values[key] = int(value.strip().split()[0])
        mem_total, mem_free = values["MemTotal"], values["MemAvailable"]
    except (OSError, ValueError, KeyError):
        pass
    memory = round((1 - mem_free / mem_total) * 100) if mem_total else 0

    return {
        "now": now,
        "agents": agents,
        "metrics": {"working": working, "ready": ready, "doneToday": done_today, "load": round(load1, 2), "memory": memory},
        "recent": sorted(tasks.values(), key=lambda t: t.get("completed_at") or t.get("started_at") or t.get("created_at") or 0, reverse=True)[:8],
    }


def make_handler(state_provider, static_dir: Path):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(static_dir), **kwargs)

        def do_GET(self):
            path = urlparse(self.path).path
            if path in {"/api/state", "/health"}:
                payload = {"ok": True} if path == "/health" else state_provider()
                body = json.dumps(payload, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path == "/":
                self.path = "/index.html"
            return super().do_GET()

        def log_message(self, fmt, *args):
            if args and str(args[0]).startswith("GET /api/state"):
                return
            super().log_message(fmt, *args)

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3001)
    args = parser.parse_args()
    mimetypes.add_type("text/javascript", ".js")
    server = ThreadingHTTPServer((args.host, args.port), make_handler(collect_state, ROOT / "public"))
    print(f"Maura Agent Office listening on http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
