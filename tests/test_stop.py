"""Tests for scripts/stop.py and its interaction with .claude/hooks/stop.py.

All tests run in a temporary project (Hebrew folder name) with copies of the
two scripts. The real project tree is never touched.
Run: python -m unittest tests.test_stop
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_SCRIPT = os.path.join(REAL, "scripts", "stop.py")
SRC_HOOK = os.path.join(REAL, ".claude", "hooks", "stop.py")
ISO = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"


class StopBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="פרויקט-")
        os.makedirs(os.path.join(self.tmp, "scripts"))
        os.makedirs(os.path.join(self.tmp, ".claude", "hooks"))
        self.script = os.path.join(self.tmp, "scripts", "stop.py")
        self.hook = os.path.join(self.tmp, ".claude", "hooks", "stop.py")
        shutil.copy(SRC_SCRIPT, self.script)
        shutil.copy(SRC_HOOK, self.hook)
        self.state = os.path.join(self.tmp, "state")
        self.stop = os.path.join(self.state, "STOP")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_stop(self, *args):
        return subprocess.run([sys.executable, "-I", self.script] + list(args),
                              capture_output=True, stdin=subprocess.DEVNULL, timeout=30)

    def run_hook(self, tool="Bash"):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        payload = json.dumps({"tool_name": tool, "tool_input": {}}).encode()
        return subprocess.run([sys.executable, "-I", self.hook], input=payload,
                              capture_output=True, env=env, timeout=30)

    def content(self):
        with open(self.stop, "rb") as f:
            return f.read()


class TestCreate(StopBase):
    def test_creates_file_and_missing_state_dir(self):
        self.assertFalse(os.path.exists(self.state))
        p = self.run_stop()
        self.assertEqual(p.returncode, 0)
        self.assertTrue(os.path.isfile(self.stop))

    def test_success_output_exact(self):
        p = self.run_stop()
        self.assertEqual(p.stdout.decode("ascii").strip(), "STOPPED: state/STOP")
        self.assertEqual(p.stderr, b"")

    def test_content_one_line_iso_without_reason(self):
        self.run_stop()
        raw = self.content()
        self.assertTrue(raw.endswith(b"\n"))
        self.assertEqual(raw.count(b"\n"), 1)
        self.assertRegex(raw.decode("utf-8").rstrip("\n"), r"^" + ISO + r"$")

    def test_content_with_reason(self):
        self.run_stop("disk full")
        self.assertRegex(self.content().decode("utf-8").rstrip("\n"), r"^" + ISO + r" disk full$")

    def test_unquoted_words_joined(self):
        self.run_stop("a", "b", "c")
        self.assertTrue(self.content().decode("utf-8").rstrip("\n").endswith(" a b c"))

    def test_no_bom(self):
        self.run_stop("x")
        self.assertFalse(self.content().startswith(b"\xef\xbb\xbf"))


class TestIdempotent(StopBase):
    def test_second_run_keeps_bytes(self):
        self.run_stop("first")
        before = self.content()
        p = self.run_stop("second")
        self.assertEqual(p.returncode, 0)
        self.assertIn("already stopped", p.stdout.decode("ascii"))
        self.assertEqual(self.content(), before)

    def test_manual_empty_file_not_overwritten(self):
        os.makedirs(self.state)
        open(self.stop, "wb").close()
        p = self.run_stop("reason")
        self.assertEqual(p.returncode, 0)
        self.assertIn("already stopped", p.stdout.decode("ascii"))
        self.assertEqual(self.content(), b"")

    def test_stop_as_directory_reports_already_stopped(self):
        os.makedirs(self.stop)
        p = self.run_stop()
        self.assertEqual(p.returncode, 0)
        self.assertIn("already stopped", p.stdout.decode("ascii"))
        self.assertTrue(os.path.isdir(self.stop))

    def test_parallel_runs_one_line(self):
        procs = [subprocess.Popen([sys.executable, "-I", self.script, "p%d" % i],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL) for i in range(4)]
        codes = [pr.wait(timeout=30) for pr in procs]
        for pr in procs:
            pr.stdout.close()
            pr.stderr.close()
        self.assertEqual(codes, [0, 0, 0, 0])
        self.assertEqual(self.content().count(b"\n"), 1)


class TestReasonText(StopBase):
    def test_hebrew_reason_utf8_in_file_ascii_on_console(self):
        reason = "עצירה דחופה"
        p = self.run_stop(reason)
        self.assertEqual(p.returncode, 0)
        text = self.content().decode("utf-8").rstrip("\n")
        self.assertTrue(text.endswith(" " + reason))
        self.assertNotIn("?", text)
        p.stdout.decode("ascii")
        p.stderr.decode("ascii")

    def test_newlines_and_control_chars_become_one_line(self):
        self.run_stop("a\nb\r\nc\x01d\te f")
        raw = self.content()
        self.assertEqual(raw.count(b"\n"), 1)
        self.assertTrue(raw.decode("utf-8").rstrip("\n").endswith(" a b c d e f"))

    def test_long_reason_truncated(self):
        self.run_stop("x" * 500)
        line = self.content().decode("utf-8").rstrip("\n")
        self.assertEqual(len(line.split(" ", 1)[1]), 200)


class TestFailure(StopBase):
    def test_state_is_a_file(self):
        open(self.state, "wb").close()
        p = self.run_stop()
        self.assertEqual(p.returncode, 1)
        self.assertIn("NOT STOPPED", p.stderr.decode("ascii"))
        self.assertEqual(p.stdout, b"")
        self.assertTrue(os.path.isfile(self.state))

    def test_output_is_ascii_on_all_paths(self):
        outs = [self.run_stop("עברית")]
        outs.append(self.run_stop("עברית"))
        shutil.rmtree(self.state)
        open(self.state, "wb").close()
        outs.append(self.run_stop("עברית"))
        for p in outs:
            p.stdout.decode("ascii")
            p.stderr.decode("ascii")

    def test_source_never_deletes(self):
        with open(SRC_SCRIPT, encoding="utf-8") as f:
            src = f.read()
        for word in ("os.remove", "os.unlink", "unlink(", "rmtree", "os.rmdir", "os.rename", "os.replace"):
            self.assertNotIn(word, src)


class TestHookIntegration(StopBase):
    def test_hook_allows_before_and_blocks_after(self):
        for tool in ("Read", "Bash", "PowerShell"):
            self.assertEqual(self.run_hook(tool).returncode, 0, tool)
        self.assertEqual(self.run_stop("halt").returncode, 0)
        for tool in ("Read", "Bash", "PowerShell"):
            p = self.run_hook(tool)
            self.assertEqual(p.returncode, 2, tool)
            self.assertIn("STOP", p.stderr.decode("utf-8", "replace"))

    def test_hook_allows_again_after_manual_removal(self):
        self.run_stop()
        self.assertEqual(self.run_hook().returncode, 2)
        os.remove(self.stop)
        self.assertEqual(self.run_hook().returncode, 0)


if __name__ == "__main__":
    unittest.main()
