"""Define interfaces for pynote."""

import subprocess, json, os
from enum import Enum
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

from .apis import DirectoryList, Notebook, Note
from ._strings import PStrings

executor = ThreadPoolExecutor(max_workers=1)


@dataclass
class Settings:
    """Settings class
    Description:
        Holds settings data
    Attributes:
        config_dir (Path): Settings Path
        settings (Dict): Settings Dict
    Returns:
        bool: Based on self.status == 200.
    Example:
        >>> example_function_call()
        expected_output
    """

    config_dir: Path = Path("~/.config/pytui").expanduser()
    config_file: Path = config_dir.joinpath("settings.json")
    settings: Dict = field(default_factory=dict)

    def load(self) -> Dict:
        """Load settings from file"""
        try:
            with open(self.config_file, "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError or json.JSONDecodeError:
            self.save(self.default())
        return self.settings

    def save(self, settings: Optional[Dict] = None) -> None:
        """Save settings to file"""
        with open(self.config_file, "w") as f:
            json.dump(settings if settings else self.settings, f)

    def default(self) -> Dict:
        """Set default settings"""
        return {
            "editor": "nvim",
            "wiki_dir": "~/wiki",
            "notebook_dir": "~/wiki/notes",
            "color_scheme": {
                "background": "#1a1b26",
                "text": "#c0caf5",
                "title": "bg:#16161e fg:#1a1b26",
                "bg1": "#24283b",
                "fg1": "#a9b1d6",
                "p1": "fg:#3d5pa1",
                "cursor": "#ff9e64",
                "hl": "#7aa2f7",
                "hl1": "#2ac3de",
                "hl2": "#bb9af7",
                "border": "#3d59a1",
                "border1": "#565f89",
                "border2": "#414868",
                "flash": "#f7768e",
            },
        }

    def __init__(self, dir: Optional[str] = None):
        """Initialize settings"""
        if dir != None:
            self.config_dir = Path(dir)
            self.config_file = self.config_dir.joinpath("settings.json")
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self.save(self.default())
        self.load()

    def __getitem__(self, key):
        return self.settings[key]

def get_term_size():
    try:
        return os.get_terminal_size()
    except OSError:
        return None

@dataclass
class State:
    directorylist: Optional[DirectoryList] = None
    settings: Settings = field(default_factory=Settings)
    notebook: Optional[Notebook] = None
    note: Optional[Note] = None
    running: bool = True
    layout: Optional[Layout] = None
    termsize: Optional[os.terminal_size] = get_term_size()
    main_window_html: str = "<h3>TEST</h3>"



@dataclass
class UI:
    """Handle UI operations
    Description:
        Contains methods for UI operations
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

    state: State = field(default_factory=State)
    main_buffer: Buffer = field(default_factory=Buffer)
    main_text_window: Window = field(default_factory=Window)
    main_layout: Layout = field(init=False)
    app: Application = field(init=False)
    kb: KeyBindings = field(default_factory=KeyBindings)

    def run(self, state: State):
        self.keybinds()
        while self.state.running:
            if self.state.layout:
                self.app.layout = self.state.layout
            else:
                self.app.layout = self.state.layout = self.master_layout()
            self.app.run()

    def __post_init__(self):
        self.style: Style = Style.from_dict(self.state.settings["color_scheme"])
        self.v_sep = Window(width=1, char="|", style="class:bg1")
        self.app: Application = Application(
            layout=self.master_layout(),
            key_bindings=self.kb,
            full_screen=True,
            style=self.style,
            refresh_interval=1,
        )

    def menu_bar(self) -> VSplit:
        self.main_menu_quit = Window(
            content=FormattedTextControl(
                text=PStrings.menu_quit,
            ),
            align=WindowAlign.LEFT,
            width=PStrings.menu_quit.__sizeof__(),
            style="class:title",
        )
        self.main_menu_help = Window(
            content=FormattedTextControl(
                text=PStrings.menu_help,
            ),
            align=WindowAlign.LEFT,
            width=PStrings.menu_help.__sizeof__(),
            style="class:title",
        )
        self.main_menu_options = Window(
            content=FormattedTextControl(
                text=PStrings.menu_options,
            ),
            align=WindowAlign.LEFT,
            width=PStrings.menu_options.__sizeof__(),
            style="class:title",
        )
        self.main_menu_notes = Window(
            content=FormattedTextControl(
                text=PStrings.menu_notes,
            ),
            align=WindowAlign.LEFT,
            width=PStrings.menu_notes.__sizeof__(),
            style="class:title",
        )
        self.main_menu_input = Window(
            content=FormattedTextControl(
                text=PStrings.std,
            ),
            align=WindowAlign.LEFT,
            width=PStrings.std.__sizeof__(),
            style="class:title",
        )
        self.main_menu_time = Window(
            content=FormattedTextControl(
                text=HTML(
                    f"<p1>  {datetime.now().date()} |   {datetime.now().strftime("%H:%M")} </p1>"
                )
            ),
            align=WindowAlign.RIGHT,
            style="class:title",
        )
        return VSplit(
            [
                self.main_menu_quit,
                self.main_menu_help,
                self.main_menu_options,
                self.main_menu_notes,
                self.main_menu_input,
                self.main_menu_time,
            ],
            height=1,
        )

    def two_window_layout(self) -> List:
        return [
            Window(content=BufferControl(buffer=self.main_buffer), style="class:bg1"),
            Window(
                content=FormattedTextControl(text="pynote v:0.1.0"), style="class:bg1"
            ),
        ]

    def buffered_window_layout(self) -> Layout:
        return Layout(
            container=HSplit(
                [
                    self.menu_bar(),
                    VSplit(
                        [
                            Window(
                                content=BufferControl(buffer=self.main_buffer),
                                style="class:bg1",
                            )
                        ]
                    ),
                ]
            )
        )

    def formatted_window_layout(self) -> Layout:
        return Layout(
            container=HSplit(
                [
                    self.menu_bar(),
                    VSplit(
                        [
                            Window(
                                content=FormattedTextControl(
                                    text=self.state.main_window_html
                                ),
                                style="class:bg1",
                            )
                        ]
                    ),
                ]
            )
        )

    def master_layout(self) -> Layout:
        wrapper = HSplit(
            [
                self.menu_bar(),
                VSplit(
                    [
                        self.two_window_layout()[0],
                        self.v_sep,
                        self.two_window_layout()[1],
                    ]
                ),
            ]
        )
        return Layout(container=wrapper)

    def keybinds(self):
        @self.kb.add("c-q")
        def exit_(event):
            self.state.running = False
            event.app.exit()

        @self.kb.add("c-n")
        async def notes(event):
            opts = f"--reverse --multi --cycle"
            note = DirectoryList(
                self.state.settings["notebook_dir"]
            ).pick_or_return_input(opts=opts)
            noteptr: Path = (
                Path(self.state.settings["wiki_dir"]).joinpath(note[0]).expanduser()
            )
            launch_nvim(noteptr)
            get_app().invalidate()

        @self.kb.add("f2")
        def options(event):
            self.state.main_window_html = "<br><br><h2>THIS IS A TEST</h2>"
            self.app.layout = self.state.layout = WindowTemplates.options(self)
            get_app().invalidate()


class WindowTemplates:
    @staticmethod
    def home(ui: UI) -> Layout:
        return ui.master_layout()

    @staticmethod
    def options(ui: UI) -> Layout:
        return ui.formatted_window_layout()


class Status(Enum):
    """Status Codes Enum

    Description:
        Enum of status codes.

    Attributes:
        OK: int 200
        CREATED: int 201
        ACCEPTED: int 202
        NO_CONTENT: int 204
        MOVED_PERMANENTLY: int 301
        FOUND: int 302
        NOT_MODIFIED: int 304
        BAD_REQUEST: int 400
        UNAUTHORIZED: int 401
        FORBIDDEN: int 403
        NOT_FOUND: int 404
        METHOD_NOT_ALLOWED: int 405
        CONFLICT: int 409
        INTERNAL_SERVER_ERROR: int 500
        NOT_IMPLEMENTED: int 501
        BAD_GATEWAY: int 502
        SERVICE_UNAVAILABLE: int 503
    """

    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503


@dataclass
class Return:
    """Return class

    Description:
        Holds status, optional return object, and message

    Attributes:
        code (Status): Return Code.
        obj (Any): Any Returnable object.
        msg (str): Return Message

    Returns:
        bool: Based on self.status == 200.

    Example:
        >>> example_function_call()
        expected_output

    """

    code: Status
    obj: Optional[Any]
    msg: str

    def __bool__(self):
        return self.code == 200


@dataclass
class CLI:
    bat: bool = which("bat") is not None
    tmux: bool = os.environ.get("TMUX") is not None
    settings: Settings = field(default_factory=Settings)

    def dir_search(self, directory: str):
        _results = DirectoryList(directory).pick_or_return_input()
        try:
            launch_nvim(_results[1])
        except IndexError:
            print("No file selected.")

    def wiki_capture(self):
        if self.bat:
            _preview = (
                f"bat --style=plain --color=always {self.settings['wiki_dir']}/{{}}"
            )
        else:
            _preview = f"cat {self.settings['wiki_dir']}/{{}}"
        if self.tmux:
            opts = f'--preview-window=up,20 --preview="{_preview}" --print-query'
        else:
            opts = (
                f'--preview-window=up,20 --border --preview="{_preview}" --print-query'
            )
        selection = DirectoryList(self.settings["notebook_dir"]).pick_or_return_input(
            opts
        )
        try:
            file_ptr = (
                Path(self.settings["notebook_dir"]).expanduser().joinpath(selection[1])
            )
        except IndexError:
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            file_ptr = (
                Path(self.settings["notebook_dir"])
                .expanduser()
                .joinpath(f"{timestamp}-{selection[0]}.wiki")
            )
            capture_template = f"= {selection[0]} =\n*Created:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n== Summary ==\nProvide a brief overview of the note here.\n\n== Main Content ==\nWrite the main content here, using *bold*, _italic_, and [[wiki links|custom descriptions]].\n\n=== Subsection Example ===\nExpand on specific topics with additional details.\n\n* Bullet list item\n* Another item\n    - Nested bullet list item\n\n1. Numbered list item\n2. Second numbered item\n\n== Tasks ==\n* [] Todo item 1\n* [] Todo item 2\n\n== Resources ==\n- [[resource link]]\n- [[reference|Optional description]]\n\n== Additional Notes ==\nAdd any extra details or reminders here.\n".encode()
            with open(file_ptr, "w") as f:
                f.write(capture_template.decode())
                f.flush()
                f.close()
        subprocess.run(
            [self.settings["editor"], file_ptr.name],
            cwd=Path(self.settings["notebook_dir"]).expanduser(),
        )


def launch_nvim(file_path: Path):
    subprocess.run(["nvim", file_path.name], cwd=file_path.parent)
    print("")
