import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from server import collect_state, make_handler


class StateTests(unittest.TestCase):
    def test_collect_state_maps_running_task_to_agent(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "kanban.db"
            con = sqlite3.connect(db)
            con.execute("CREATE TABLE tasks (id TEXT, title TEXT, assignee TEXT, status TEXT, priority INTEGER, created_at INTEGER, started_at INTEGER, completed_at INTEGER)")
            con.execute("INSERT INTO tasks VALUES ('t1','Menulis artikel','maura-trans-internal','running',10,1,2,NULL)")
            con.commit(); con.close()

            state = collect_state([db], now=10)

            trans = next(a for a in state["agents"] if a["id"] == "maura-trans-internal")
            self.assertEqual(trans["status"], "working")
            self.assertEqual(trans["task"]["title"], "Menulis artikel")
            self.assertEqual(state["metrics"]["working"], 1)

    def test_collect_state_deduplicates_tasks_across_databases(self):
        with tempfile.TemporaryDirectory() as td:
            paths = []
            for name in ("a.db", "b.db"):
                db = Path(td) / name
                con = sqlite3.connect(db)
                con.execute("CREATE TABLE tasks (id TEXT, title TEXT, assignee TEXT, status TEXT, priority INTEGER, created_at INTEGER, started_at INTEGER, completed_at INTEGER)")
                con.execute("INSERT INTO tasks VALUES ('same','Task','default','done',1,1,2,9)")
                con.commit(); con.close(); paths.append(db)

            state = collect_state(paths, now=10)

            self.assertEqual(state["metrics"]["doneToday"], 1)

    def test_make_handler_serves_api_json(self):
        handler = make_handler(lambda: {"ok": True}, Path("."))
        self.assertTrue(callable(handler))

    def test_office_static_module_path_strips_reverse_proxy_prefix(self):
        handler = make_handler(lambda: {"ok": True}, Path("."))
        self.assertEqual(handler.normalized_static_path("/office/idle-wandering.mjs"), "/idle-wandering.mjs")
        self.assertEqual(handler.normalized_static_path("/office/"), "/index.html")


if __name__ == "__main__":
    unittest.main()
