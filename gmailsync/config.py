from configparser import ConfigParser
from logging.config import dictConfig
import os


def sanitize_path(path):
    return os.path.abspath(os.path.expanduser(path))


class Config:

    def __init__(self):
        self.token = sanitize_path('~/.gmailsync-token.pickle')
        self.box_type = 'maildir'
        self.log_file = None
        self.channels = {}
        self.groups = {}

    def add_channel(self, channel):
        self.channels[channel.name] = channel

    def add_group(self, group):
        self.groups[group.name] = group

    def get_channels(self, names):
        if not names:
            return self.channels.values()

        channels = []
        for name in names:
            if name in channels:
                channels.append(self.channels[name])
            elif name in groups:
                channels.extend([channels[c] for c in self.groups[name].channels])
            else:
                # TODO: show error
                pass


class Channel:
    def __init__(self):
        self.name = None
        self.local = None
        self.remote = None
        self.box_type = None


class Group:
    def __init__(self):
        self.name = None
        self.channels = []


class ConfigReader:
    def load_config(self, conf_path):
        parser = ConfigParser()
        parser.read(sanitize_path(conf_path))

        config = Config()

        if parser.has_section('general'):
            if parser.has_option('general', 'token'):
                config.token = parser.get('general', 'token')
            if parser.has_option('general', 'box_type'):
                config.box_type = parser.get('general', 'box_type')
            if parser.has_option('general', 'log_file'):
                config.log_file = sanitize_path(parser.get('general', 'log_file'))

        for section in parser.sections():
            if section.startswith('channel-'):
                channel = self._parse_channel(parser, section, config.box_type)
                config.add_channel(channel)

            if section.startswith('group-'):
                group = self._parse_group(parser, section)
                config.add_group(group)

        return config

    def _parse_channel(self, parser, section, default_box_type):
        channel = Channel()
        channel.name = section.split('channel-', 1)[1]
        # TODO: validate local and remote are present -> mandatory
        channel.local = sanitize_path(parser.get(section, 'local'))
        channel.remote = parser.get(section, 'remote')
        if parser.has_option(section, 'box_type'):
            channel.box_type = parser.get(section, 'box_type')
        else:
            channel.box_type = default_box_type
        return channel

    def _parse_group(self, parser, section):
        group = Group()
        group.name = section.split('group-', 1)[1]
        # TODO: validate channels is present -> mandatory
        channels = parser.get(section, 'channels').split(',')
        for channel in channels:
            # TODO: validate channel startswith 'channel-'
            group.channels.append(channel.strip())
        return group


def set_up_logger(verbose, log_file):
    if log_file is not None:
        LOGGING['handlers']['file']['filename'] = log_file
        LOGGING['loggers']['gmailsync']['handlers'].append('file')
    else:
        del LOGGING['handlers']['file']

    if verbose:
        LOGGING['loggers']['gmailsync']['level'] = 'DEBUG'

    dictConfig(LOGGING)


# Logging config
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s'
        },
    },
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': None,
            'mode': 'a',
            'maxBytes': 104857600, # 100 MB
            'backupCount': 500, # 500 files
        }
    },
    'loggers': {
        'gmailsync': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}
