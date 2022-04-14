import os
from pathlib import Path
import logging
import logging.handlers

from .parser import EnhancedConfigParser
from .loader import ConfigLoader
from .models import CONFIG_FILENAME
from .validator import ConfigValidator, ConfigurationError


__all__ = [
    'load_config', 'set_up_logger', 'get_default_config_file', 'ConfigurationError'
]


def load_config(config_file):
    if not os.path.isfile(config_file):
        raise ConfigurationError('Configuration file does not exist: {}'.format(config_file))

    parser = EnhancedConfigParser()
    parser.read(config_file)

    loader = ConfigLoader(parser, get_config_dir())
    config = loader.load()

    validator = ConfigValidator()
    validator.validate(config)

    return config


def get_config_dir():
    xdg_config_dir = os.environ.get('XDG_CONFIG_HOME') or os.path.join(Path.home(), '.config')
    xdg_config_gmailsync = os.path.join(xdg_config_dir, 'gmailsync')
    if os.path.isdir(xdg_config_gmailsync):
        return xdg_config_gmailsync
    else:
        return os.path.join(Path.home(), '.gmailsync')


def get_default_config_file():
    return os.path.join(get_config_dir(), CONFIG_FILENAME)


def set_up_logger(verbose, config=None):
    logger = logging.getLogger('gmailsync')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    formatter = logging.Formatter(config.format)

    handlers = []

    console_handler = logging.StreamHandler()
    handlers.append(console_handler)

    if config.file is not None:
        file_handler = logging.handlers.RotatingFileHandler(config.file,
            maxBytes=config.max_bytes, backupCount=config.backup_count)
        handlers.append(file_handler)

    for handler in handlers:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
