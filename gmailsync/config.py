from configparser import ConfigParser
import logging
import logging.handlers
import os


def to_path(value, is_file=False, can_read=False):
    path = os.path.abspath(os.path.expanduser(value))
    if is_file:
        if not os.path.isfile(path):
            raise ValidationError('Invalid value in config file. <' + value + '> should be a valid file')
        if can_read and not os.access(path, os.R_OK):
            raise ValidationError('Invalid value in config file. <' + value + '> should be a readable file. Check permissions')
    return path


def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValidationError('Invalid value in config file. <' + value + '> should be an int')


class Config:

    def __init__(self):
        self.credentials = to_path('~/.gmailsync-credentials.json', is_file=True, can_read=True)
        self.token = to_path('~/.gmailsync-token.pickle')
        self.box_type = 'maildir'
        self.logger_config = None
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
                raise ValueError("Channel '" + name + "' is not present in config file")


class ChannelConfig:

    def __init__(self):
        self.name = None
        self.mailbox_path = None
        self.query = None
        self.box_type = None


class GroupConfig:

    def __init__(self):
        self.name = None
        self.channels = []


class LoggerConfig:

    def __init__(self):
        self.file = None
        self.file_max_bytes = 104857600 # 100 MB
        self.file_backup_count = 500 # 500 files
        self.format = '%(asctime)s %(levelname)s [%(name)s] %(message)s'


class ConfigReader:

    def load_config(self, conf_path):
        parser = ConfigParser()
        parser.read(to_path(conf_path))

        config = Config()

        if parser.has_section('general'):
            if parser.has_option('general', 'credentials'):
                config.credentials = parser.get('general', 'credentials')
            if parser.has_option('general', 'token'):
                config.token = parser.get('general', 'token')
            if parser.has_option('general', 'box_type'):
                config.box_type = parser.get('general', 'box_type')

        config.logger_config = self._parse_logger_config(parser)

        for section in parser.sections():
            if section.startswith('channel-'):
                channel = self._parse_channel(parser, section, config.box_type)
                config.add_channel(channel)

            if section.startswith('group-'):
                group = self._parse_group(parser, section)
                config.add_group(group)

        return config

    def _parse_channel(self, parser, section, default_box_type):
        channel = ChannelConfig()
        channel.name = section.split('channel-', 1)[1]
        channel.mailbox_path = to_path(parser.get(section, 'mailbox'))
        channel.query = parser.get(section, 'query')
        if parser.has_option(section, 'box_type'):
            channel.box_type = parser.get(section, 'box_type')
        else:
            channel.box_type = default_box_type
        return channel

    def _parse_group(self, parser, section):
        group = GroupConfig()
        group.name = section.split('group-', 1)[1]
        channels = [channel.strip() for channel in parser.get(section, 'channels').split(',')]
        for channel in channels:
            if not channel.startswith('channel-') or not parser.has_section(channel):
                raise ValueError("'channels' section in '" + section + "' must contain a "\
                    "comma-separated list of valid channels")
            group.channels.append(channel.strip())
        return group

    def _parse_logger_config(self, parser):
        logger_config = LoggerConfig()
        if parser.has_option('log', 'file'):
            logger_config.file = to_path(parser.get('log', 'file'))
        if parser.has_option('log', 'file_max_bytes'):
            logger_config.file_max_bytes = to_int(parser.get('log', 'file_max_bytes'))
        if parser.has_option('log', 'file_backup_count'):
            logger_config.file_backup_count = to_int(parser.get('log', 'file_backup_count'))
        if parser.has_option('log', 'format'):
            logger_config.format = parser.get('log', 'format')
        return logger_config


def set_up_logger(verbose, conf=None):
    logger = logging.getLogger('gmailsync')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    formatter = logging.Formatter(conf.format)

    handlers = []

    console_handler = logging.StreamHandler()
    handlers.append(console_handler)

    if conf.file is not None:
        file_handler = logging.handlers.RotatingFileHandler(conf.file,
            maxBytes=conf.file_max_bytes, backupCount=conf.file_backup_count)
        handlers.append(file_handler)

    for handler in handlers:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)