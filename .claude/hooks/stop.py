import sys
import json


def main():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(here))
    json.load(sys.stdin)  # fail closed: invalid input blocks the call
    stop_file = os.path.join(root, "state", "STOP")
    if os.path.exists(stop_file):
        sys.stderr.write("STOP is active (state/STOP exists). All tool calls are blocked. "
                         "A human must delete state/STOP.\n")
        return 2
    return 0


try:
    code = main()
except BaseException as e:
    sys.stderr.write("stop.py internal error, failing closed: %s\n" % type(e).__name__)
    code = 2
sys.exit(code)
