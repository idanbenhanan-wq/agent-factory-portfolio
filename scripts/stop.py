"""Create state/STOP, the kill switch checked by .claude/hooks/stop.py.

Usage: python -I scripts/stop.py ["reason"]

Creates state/STOP with one line: UTC ISO time, plus the reason if given.
If state/STOP already exists it is not touched ("already stopped", exit 0).
This script never deletes anything. A human removes the file manually:
    Remove-Item state\\STOP

Exit codes: 0 stopped or already stopped, 1 could not create the file.
Console output is ASCII only. The file itself is UTF-8 without BOM.
"""
import os
import sys
import unicodedata
from datetime import datetime, timezone

MAX_REASON = 200


def clean(text):
    out = []
    for ch in text:
        out.append(" " if unicodedata.category(ch).startswith(("C", "Z")) else ch)
    return " ".join("".join(out).split())[:MAX_REASON]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state = os.path.join(root, "state")
    target = os.path.join(state, "STOP")
    reason = clean(" ".join(sys.argv[1:]))
    line = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if reason:
        line += " " + reason
    data = (line + "\n").encode("utf-8")
    try:
        os.makedirs(state, exist_ok=True)
        if os.path.lexists(target):
            print("already stopped: state/STOP")
            return 0
        fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
    except FileExistsError:
        if os.path.lexists(target):
            print("already stopped: state/STOP")
            return 0
        sys.stderr.write("NOT STOPPED: FileExistsError\n")
        return 1
    except OSError as e:
        sys.stderr.write("NOT STOPPED: %s\n" % type(e).__name__)
        return 1
    print("STOPPED: state/STOP")
    return 0


try:
    code = main()
except BaseException as e:
    sys.stderr.write("NOT STOPPED: %s\n" % type(e).__name__)
    code = 1
sys.exit(code)
