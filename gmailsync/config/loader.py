from .parser import NoSectionError, NoOptionError
from .models import Config, ChannelConfig, GroupConfig, LoggerConfig
from .validator import ConfigurationError


VALID_SECTIONS = ('general', 'log')  # And channel-* and group-*


class ConfigLoader:

    def __init__(self, parser, default_config_dir):
        self.parser = parser
        self.default_config_dir = default_config_dir

    def load(self):
        try:
            credentials = self.parser.getpath('general', 'credentials', is_file=True, readable=True, fallback=None)
            token = self.parser.getpath('general', 'token', fallback=None)
            box_type = self.parser.get('general', 'box_type', fallback=None)

            channels = {}
            groups = {}

            for section in self.parser.sections():
                if section.startswith('channel-'):
                    channel = self._parse_channel(section)
                    channels[channel.name] = channel

                elif section.startswith('group-'):
                    group = self._parse_group(section)
                    groups[group.name] = group

                elif section not in VALID_SECTIONS:
                    raise ConfigurationError("Invalid section name: '{}'".format(section))

            logger_config = self._parse_logger_config()

            config = Config(credentials=credentials,
                            token=token,
                            box_type=box_type,
                            channels=channels,
                            groups=groups,
                            logger_config=logger_config,
                            default_config_dir=self.default_config_dir)

            return config

        except ConfigurationError:
            raise
        except (NoSectionError, NoOptionError, ValueError) as e:
            raise ConfigurationError(e.message)

    def _parse_channel(self, section):
        name = self._extract_name(section, prefix='channel-')
        mailbox_path = self.parser.getpath(section, 'mailbox')
        query = self.parser.get(section, 'query', fallback=None)
        box_type = self.parser.get(section, 'box_type', fallback=None)
        return ChannelConfig(name=name, mailbox_path=mailbox_path, query=query, box_type=box_type)

    def _parse_group(self, section):
        name = self._extract_name(section, prefix='group-')
        channels = self.parser.getlist(section, 'channels')
        return GroupConfig(name=name, channels=channels)

    def _parse_logger_config(self):
        file = self.parser.getpath('log', 'file', fallback=None)
        max_bytes = self.parser.getint('log', 'file_max_bytes', fallback=None)
        backup_count = self.parser.getint('log', 'file_backup_count', fallback=None)
        format = self.parser.get('log', 'format', fallback=None)
        return LoggerConfig(file=file, max_bytes=max_bytes, backup_count=backup_count, format=format)

    def _extract_name(self, value, prefix):
        if not value.startswith(prefix):
            raise ConfigurationError('Invalid section name. It must start with {!r}'.format(prefix))
        return value.split(prefix, 1)[1].strip()
