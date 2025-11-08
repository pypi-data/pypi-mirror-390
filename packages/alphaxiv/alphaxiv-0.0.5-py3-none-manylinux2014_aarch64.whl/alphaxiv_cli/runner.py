import os
import sys

def main():
    # The executable is placed in the same directory as this script.
    executable_path = os.path.join(os.path.dirname(__file__), "alphaxiv-executable")

    if not os.path.exists(executable_path):
        print(f"Error: Executable not found at {executable_path}", file=sys.stderr)
        sys.exit(1)

    # Set executable permissions if they aren't not already set
    if not os.access(executable_path, os.X_OK):
        os.chmod(executable_path, 0o755)

    # Pass all command-line arguments to the executable
    os.execv(executable_path, [executable_path] + sys.argv[1:])
