"""Set up IPython testing environment for this module."""

import os
import shutil
import sys


def restart():
    from src.libs.interface import DirectoryList, FzF, Terminal
    from src.libs.objects import Return, Status

    """Restart ipython REPL."""
    os.execv(sys.executable, ["python"] + sys.argv)


banner_title = "ipython dev env".center(shutil.get_terminal_size().columns)
print(banner_title)
print(
    "Available structs: Return, Status, Fzf, DirectoryList\nAvailable commands: restart()"
)
