"""
Utilities to work with command line interfaces through terminal emulators.
"""

BOLD = '\033[1m'
RESET = '\033[0m'

COLORS = {
    'grey': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
}

COLORS['success'] = COLORS['green'] + BOLD
COLORS['warning'] = COLORS['yellow'] + BOLD
COLORS['error'] = COLORS['red'] + BOLD


def cprint(text, color=None, **kwargs):
    """ Print colorized text.
    """
    if color is not None and color in COLORS:
        print('{}{}{}'.format(COLORS[color], text, RESET), **kwargs)
    else:
        print(text, **kargs)
