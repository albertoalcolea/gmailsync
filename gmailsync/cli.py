"""
Utilities to work with command line interfaces through terminal emulators.
"""

COLORS = {
    'grey': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_grey': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
}

BOLD = '\033[1m'
RESET = '\033[0m'

STATUSES = {
    'success': COLORS['green'],
    'warning': COLORS['yellow'],
    'error': COLORS['red'],
}


def color_text(text, color, bold=False):
    """
    Add ANSI escape sequence to color :param text with :param color color.
    """
    if bold:
        return '{}{}{}{}'.format(color, BOLD, text, RESET)
    else:
        return '{}{}{}'.format(color, text, RESET)


def cprint(text, status=None, color=None, bold=False, **kwargs):
    """
    Print colorized text.

    :param text: text to be colored.
    :param status: standard status as a string: ('success', 'warning' or 'error').
    If defined, :param color and :param bold will be ignored.
    :param color: color to color the text.
    :param bold: if `True` the special escape sequence to print the text in bold will be added.
    :param **kwargs: optional keyword arguments supported by `print` function.
    """
    if status is not None and status in STATUSES:
        print(color_text(text, STATUSES[status], bold=True), **kwargs)
    elif color is not None and color in COLORS:
        print(color_text(text, COLORS[color], bold=bold), **kwargs)
    else:
        print(text, **kwargs)