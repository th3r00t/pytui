#!/usr/bin/env python
"""Entry point for pynote."""
import argparse
from libs.interface import UI, Settings, CLI, State, WindowTemplates

parser = argparse.ArgumentParser(description="pynote")
parser.add_argument("-d", "--directory", help="Directory to list")
parser.add_argument("-n", "--notes", action="store_true", help="List notes")
args = parser.parse_args()
settings = Settings()
state: State = State(settings=settings, layout=WindowTemplates.home(UI()))


if __name__ == "__main__":
    if args.directory:
        print(CLI().dir_search(args.directory))
    if args.notes:
        CLI().wiki_capture()
    else:
        UI().run(state)
