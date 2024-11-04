"""Set up IPython testing environment for this module."""

import os
import shutil
import sys

# from pathlib import Path
# from pprint import pprint


def restart():
    """Restart ipython REPL."""
    os.execv(sys.executable, ["python"] + sys.argv)


banner_title = "ipython dev env".center(shutil.get_terminal_size().columns)
print(banner_title)
print("Available structs: ud, df, ep\nAvailable commands: restart()")
print("Testing UserShell(ud)")
