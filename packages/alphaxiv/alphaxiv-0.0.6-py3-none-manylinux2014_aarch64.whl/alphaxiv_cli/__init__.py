import os
import sys

def main():
    executable_path = os.path.join(os.path.dirname(__file__), "alphaxiv")
    if os.path.exists(executable_path):
        os.execv(executable_path, ["alphaxiv"] + sys.argv[1:])
    else:
        print("Error: alphaxiv executable not found.", file=sys.stderr)
        sys.exit(1)
