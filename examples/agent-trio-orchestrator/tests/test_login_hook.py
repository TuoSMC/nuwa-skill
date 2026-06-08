import unittest

from scripts import login_hook


class LoginHookTests(unittest.TestCase):
    def test_wake_forwards_yes_health_and_login_if_needed(self):
        parser = login_hook.build_parser()
        args = parser.parse_args(["wake"])

        forwarded = login_hook.forwarded_args(args)

        self.assertEqual(forwarded[:4], ["wake", "--yes", "--health", "--login-if-needed"])

    def test_smoke_forwards_login_and_smoke_flags(self):
        parser = login_hook.build_parser()
        args = parser.parse_args(["smoke", "--agent", "adam"])

        forwarded = login_hook.forwarded_args(args)

        self.assertEqual(forwarded[:3], ["health", "--login-if-needed", "--smoke"])
        self.assertIn("--agent", forwarded)
        self.assertIn("adam", forwarded)
        self.assertIn("--smoke-timeout", forwarded)


if __name__ == "__main__":
    unittest.main()
