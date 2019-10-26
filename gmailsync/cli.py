"""
Utilities to work with command line interfaces through terminal emulators.
"""

from enum import Enum


class Color(Enum):
    GREY = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_GREY = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'



class Status(Enum):
    SUCCESS = Color.GREEN
    WARNING = Color.YELLOW
    ERROR = Color.RED


BOLD = '\033[1m'
RESET = '\033[0m'


def color_text(text, color=None, bold=False):
    """
    Add ANSI escape sequences to color :param text.

    :param text: text to be colored.

    :param color: optional item of 'Color' enum with the color to color the text.
    If not defined, default color will be used.

    :param bold: if `True` the special escape sequence to print the text in bold will be added.

    """
    if color is not None and not isinstance(color, Color):
        raise ValueError("'color' must be an item of 'Color' enum")

    colored = []

    if color is not None:
        colored.append(color.value)

    if bold:
        colored.append(BOLD)

    colored.append(text)

    if color is not None or bold:
        colored.append(RESET)

    return ''.join(colored)


def cprint(text, color=None, status=None, bold=False, **kwargs):
    """
    Print colorized text.

    :param text: text to be colored.

    :param color: optional item of 'Color' enum with the color to color the text.
    If not defined, default color will be used.

    :param status: optional item of 'Status' enum.
    If defined, :param color and :param bold will be ignored.

    :param bold: if `True` the special escape sequence to print the text in bold will be added.

    :param **kwargs: optional keyword arguments supported by `print` function.

    """
    if status is not None and not isinstance(status, Status):
        raise ValueError("'status' must be an item of 'Status' enum")

    if status is not None:
        colored = color_text(text, status.value, bold=True)
    else:
        colored = color_text(text, color, bold=bold)

    print(colored, **kwargs)