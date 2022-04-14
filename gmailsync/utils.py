import itertools
import os


def chunked(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk


def expand_path(path):
    """
    Convert relative paths to absolute paths expanding environment variables, and '~' to
    represent the user $HOME directory in filenames.

    :param path: path to be expanded.

    """
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
