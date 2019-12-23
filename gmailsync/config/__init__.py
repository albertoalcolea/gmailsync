import logging
import logging.handlers

from .parser import EnhancedConfigParser
from .loader import ConfigLoader
from .validator import ConfigValidator, ConfigurationError


__all__ = [
    'load_config', 'set_up_logger', 'ConfigurationError'
]


def load_config(config_path):
    parser = EnhancedConfigParser()
    parser.read(config_path)

    loader = ConfigLoader(parser)
    config = loader.load()

    validator = ConfigValidator()
    validator.validate(config)

    return config


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