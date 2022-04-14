from configparser import RawConfigParser, _UNSET
import os

from ..utils import expand_path


class EnhancedConfigParser(RawConfigParser):
    """
    Enhanced version of RawConfigParser.

    Improvements over the original version:
      - Expansion of relative paths, environment variables and $HOME directory (~) in filenames.
      - Support to get and validate paths.
      - Support to get and validate lists.

    """

    def read(self, filenames, encoding=None):
        """
        Read and parse a filename or an iterable of filenames.

        Convert relative paths to absolute paths expanding environment variables, and '~' to
        represent the user $HOME directory in filenames.

        """
        if isinstance(filenames, (str, bytes, os.PathLike)):
            filenames = [filenames]
        expanded = []
        for filename in filenames:
            expanded.append(expand_path(filename))
        return super().read(expanded, encoding)

    def getpath(self, section, option, *, is_file=False, is_dir=False, readable=False,
                writable=False, raw=False, vars=None, fallback=_UNSET, **kwargs):
        """
        Like get(), but validating that the value is a valid path.

        Convert relative paths to absolute paths expanding environment variables, and '~' to
        represent the user $HOME directory in filenames.

        :param is_file: validate that the path is an existing file.

        :param is_dir: validate that the path is an existing directory.

        :param readable: validate that the path is reeadable. Use together with is_file or is_dir.

        :param readable: validate that the path is reeadable. Use together with is_file or is_dir.

        """
        if (readable or writable) and not (is_file or is_dir):
            raise ValueError("'readable' and 'writable' options are available only with 'is_file' or 'is_dir'")

        value = self.get(section, option, raw=raw, vars=vars, fallback=fallback, **kwargs)

        # Fast path if fallback is None
        if value is None:
            return None

        path = expand_path(value)

        access_mode = 0
        if is_file:
            access_mode |= os.F_OK
        if is_dir:
            # To read or write files inside a directory the path must be executable
            access_mode |= os.F_OK | os.X_OK

        if is_file and not os.path.isfile(path):
            raise ValueError('Path must be an existing file: {!r}'.format(value))
        if is_dir and not os.path.isdir(path):
            raise ValueError('Path must be an existing directory: {!r}'.format(value))
        if readable and not os.access(path, access_mode | os.R_OK):
            raise ValueError('Path must be readable. Check permissions: {!r}'.format(value))
        if writable and not os.access(path, access_mode | os.W_OK):
            raise ValueError('Path must be writable. Check permissions: {!r}'.format(value))

        return path

    def getlist(self, section, option, *, sep=",", raw=False, vars=None, fallback=_UNSET, **kwargs):
        """
        Like get(), but convert value to a list.

        :param sep: separator of the elements of the list.

        """
        value = self.get(section, option, raw=raw, vars=vars, fallback=fallback, **kwargs)

        # Fast path if fallback is None
        if value is None:
            return None

        return [item.strip() for item in value.split(sep)]
