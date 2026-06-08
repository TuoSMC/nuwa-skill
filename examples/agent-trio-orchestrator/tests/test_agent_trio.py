import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import agent_trio


class AgentTrioTests(unittest.TestCase):
    def make_fake_exe(self, body):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "fake"
        path.write_text("#!/usr/bin/env sh\n" + body + "\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return str(path)

    def test_eva_probe_reports_ok_when_grok_models_succeeds(self):
        fake = self.make_fake_exe(
            'if [ "$1" = "models" ]; then echo "grok-build"; exit 0; fi; exit 9'
        )
        with mock.patch.dict(os.environ, {"GROK_BIN": fake}):
            result = agent_trio.probe_eva(False, 1, 1)
        self.assertEqual(result.status, "ok")
        self.assertIn("grok models", result.detail)

    def test_adam_probe_reports_auth_needed_when_not_logged_in(self):
        fake = self.make_fake_exe(
            'if [ "$1 $2" = "auth status" ]; then echo \'{"loggedIn": false}\'; exit 0; fi; exit 9'
        )
        with mock.patch.dict(os.environ, {"CLAUDE_BIN": fake}):
            result = agent_trio.probe_adam(False, 1, 1)
        self.assertEqual(result.status, "auth-needed")
        self.assertFalse(result.login_attempted)

    def test_wake_writes_activation_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "activation.json"
            with mock.patch.object(agent_trio, "ACTIVATION_FILE", target):
                written = agent_trio.write_activation(True, source="test")
            data = json.loads(written.read_text(encoding="utf-8"))
        self.assertTrue(data["enabled"])
        self.assertEqual(data["source"], "test")
        self.assertIn("eva", data["agents"])


if __name__ == "__main__":
    unittest.main()
