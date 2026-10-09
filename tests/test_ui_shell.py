import re
import unittest
from pathlib import Path


HTML = (Path(__file__).parents[1] / "public" / "index.html").read_text()


class MissionControlShellTests(unittest.TestCase):
    def test_shell_has_accessible_navigation_and_live_panel_tabs(self):
        required = (
            'class="mission-header"',
            'id="nav-toggle"',
            'aria-controls="nav-drawer"',
            'id="nav-drawer"',
            'id="mission-panel"',
            'role="tablist"',
            'data-panel-tab="crew"',
            'data-panel-tab="stats"',
            'data-panel-tab="activity"',
            'id="panel-crew"',
            'id="panel-stats"',
            'id="panel-activity"',
            'id="crew-list"',
            'id="activity-list"',
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, HTML)

    def test_existing_actions_and_room_views_remain_available(self):
        for element_id in (
            "tasks-drawer", "create-task-drawer", "chat-drawer",
            "fab-tasks", "fab-create", "fab-chat",
        ):
            self.assertIn(f'id="{element_id}"', HTML)
        self.assertIn('class="room-views"', HTML)
        rooms = re.findall(r'data-room="([^"]+)"', HTML)
        self.assertTrue(rooms, "room tabs must survive the shell rework")
        views = HTML[HTML.index("const roomViews"):HTML.index("};", HTML.index("const roomViews"))]
        missing = [room for room in rooms if f"{room}:" not in views]
        self.assertEqual(missing, [], f"room tabs without a camera view: {missing}")


if __name__ == "__main__":
    unittest.main()
