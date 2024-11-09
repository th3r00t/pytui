"""Define interfaces for pynote."""

import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from shutil import which
from typing import Any, Dict, List, Optional

from prompt_toolkit import Application
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer, WordCompleter
from prompt_toolkit.formatted_text import HTML, to_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style
from pygments.lexers.html import HtmlLexer

# from .interface import PStrings, Settings, Status

executor = ThreadPoolExecutor(max_workers=1)
fzfUrl = "https://github.com/junegun/fzf"


class FzF:
    def __init__(self, fzfpath: Optional[str] = None):
        if fzfpath:
            self.path: str = fzfpath
        elif not which("fzf") and not fzfpath:
            raise SystemError(f"Cannot find 'fzf' on PATH. {fzfUrl}")
        else:
            self.path: str = "fzf"

    def prompt(
        self, choices: List, opts: Optional[str] = "", delimiter: str = "\n"
    ) -> List:
        selection: List = []
        choices_str: str = delimiter.join(map(str, choices))
        with tempfile.NamedTemporaryFile(delete=False) as input_file:
            with tempfile.NamedTemporaryFile(delete=False) as output_file:
                input_file.write(choices_str.encode("utf-8"))
                input_file.flush()

        os.system(f'{self.path} {opts} < "{input_file.name}" > "{output_file.name}"')

        with open(output_file.name, encoding="utf-8") as f:
            for line in f:
                selection.append(line.strip("\n"))

        os.unlink(input_file.name)
        os.unlink(output_file.name)

        return selection


@dataclass
class tkList:
    obj: List

    def __init__(self, obj: List):
        self.obj = obj

    def picker(self):
        return FzF().prompt(self.obj)

    def pick_or_return_input(self, opts: Optional[str] = ""):
        return FzF().prompt(choices=self.obj, opts=opts)


@dataclass
class DirectoryList(tkList):
    path: Path

    def __init__(self, path: str = "."):
        self.path = Path(path).expanduser()
        self.obj = self.get_list()

    def get_list(self, d=None) -> List:
        _list = []
        if d != None:
            path = Path(d)
        else:
            path = self.path

        for i in path.iterdir():
            if i.is_dir():
                for _i in self.get_list(i):
                    _list.append(f"{path.name}/{i.name}/{_i}")
            else:
                _list.append(f"{path.name}/{i.name}")

        return _list


@dataclass
class Note:
    """Note class
    Description:
        Holds note data
    Attributes:
        title (str): Note Title
        content (str): Note Content
        tags (List): Note Tags
    Returns:
    Example:
        >>> example_function_call()
        expected_output
    """

    path: Path
    title: str
    content: str
    tags: list


@dataclass
class Notebook:
    """Notebook class
    Description:
        Holds notebook data
    Attributes:
        path (Path): Notebook Path
        notes (List): List of Notes
    Example:
        >>> example_function_call()
        expected_output
    """

    path: Path
    dir_list: DirectoryList
    notes: Optional[List[Note]]

    def __init__(self, path: Path):
        self.path = path
        self.dir_list = DirectoryList(self.path.name)
        self.notes = None


class Terminal:
    """Handle terminal operations

    Description:
        Contains methods for terminal operations

    Attributes:
        attribute_name1 (type): Description of attribute_name1.
        attribute_name2 (type): Description of attribute_name2.

    Methods:
        method_name1(): Description of method_name1.
        method_name2(args): Description of method_name2.

    Args:
        param_name1 (type): Description of param_name1.
        param_name2 (type): Description of param_name2.

    Keyword Args:
        kwarg_name1 (type, optional): Description of kwarg_name1.

    Returns:
        return_type: Description of the return value.

    Raises:
        ExceptionName: Condition that raises this exception.

    Yields:
        yield_type: Description of yielded value and state.

    Example:
        >>> example_function_call()
        expected_output

    """

    def __init__(self):
        self.settings = Settings()
        self.style = Style.from_dict(self.settings["color_scheme"])

    def prompt(self, prompt_str: Optional[Any] = None, completer: Optional[Any] = []):
        if not prompt_str:
            prompt_str = PStrings.std
        if not completer:
            completer = []
        completer = WordCompleter(completer)
        return prompt(
            prompt_str,
            style=self.style,
            lexer=PygmentsLexer(HtmlLexer),
            completer=completer,
            complete_in_thread=True,
            complete_while_typing=True,
        )

    def print(self, msg: Any, colors: Optional[Dict] = None):
        print(HTML(msg), style=self.style)
