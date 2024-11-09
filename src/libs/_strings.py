from dataclasses import dataclass
from prompt_toolkit.formatted_text import HTML


@dataclass
class PStrings:
    std: HTML = HTML("<p1>pyTui  : > </p1>")
    menu_quit: HTML = HTML("<p1> C-q: 󰗼 Quit</p1>")
    menu_help: HTML = HTML("<p1>F1: 󰋖 Help</p1>")
    menu_options: HTML = HTML("<p1>F2:  Options</p1>")
    menu_notes: HTML = HTML("<p1>C-n:  Notes</p1>")
