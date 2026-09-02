"""Package execution entry point for `python -m aria`."""

import sys

from aria.cli import main

if __name__ == "__main__":
    sys.exit(main())
