"""
Models to represent the configuration and its subconfigurations.
"""
from ..utils import expand_path


DEFAULT_CRED_PATH = '~/.gmailsync-credentials.json'
DEFAULT_TOKEN_PATH = '~/.gmailsync-token.pickle'
DEFAULT_BOX_TYPE = 'maildir'

DEFAULT_LOG_MAX_BYTES = 104857600 # 100 MB
DEFAULT_LOG_BACKUP_COUNT = 500 # 500 files
DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'


class BaseConfig:

    def _get(self, value, default=None):
        """
        Shortcut to get the given :param value or :param default if value is None

        """
        return default if value is None else value


class ChannelConfig(BaseConfig):
    """
    Configuration of a channel.

    :param name: channel name.

    :param mailbox_path: path where to store the messages.

    :param query: query used to retrieve the messages. Supports the same query format as the
    Gmail search box.

    :param box_type: mailbox type. If it is not defined, the default one defined in Config will
    be used.

    """

    def __init__(self, name, mailbox_path, query, box_type=None):
        self.name = name
        self.mailbox_path = expand_path(mailbox_path)
        self.query = query
        self.box_type = box_type

    def __str__(self):
        return 'ChannelConfig <{!r}>'.format(self.name)


class GroupConfig(BaseConfig):
    """
    Configuration of a group of channels

    :param name: group name.

    :param channels: list or tuple of channel names.

    """

    def __init__(self, name, channels):
        self.name = name
        self.channels = channels

    def __str__(self):
        return 'GroupConfig <{!r}>'.format(self.name)


class LoggerConfig(BaseConfig):
    """
    Configuration of the logger.

    :param file: path of the file where to store the log messages.

    :param max_bytes: max bytes before rotate the file.

    :param backup_count: max number of files to keep on disk.

    :param format: log format.

    """

    def __init__(self, file=None, max_bytes=None, backup_count=None, format=None):
        self.file = expand_path(file) if file is not None else None
        self.max_bytes = self._get(max_bytes, default=DEFAULT_LOG_MAX_BYTES)
        self.backup_count = self._get(backup_count, default=DEFAULT_LOG_BACKUP_COUNT)
        self.format = self._get(format, default=DEFAULT_LOG_FORMAT)


class Config(BaseConfig):
    """
    Configuration of gmailsync.

    Used to configure the other components of the applications.

    :param credentials: path of the json file with the credentials of your App registered
    in Google API Console.

    :param token: path of the file where to store and read the token of the Google account
    which to synchronize messages. It will be automatically generated if it does not exist.

    :param box_type: default mailbox type. It will the mailbox type of the channels if they do
    not define a different one explicitly.

    :param channels: dict, list or tuple of ChannelConfig objects. If dict: key=name, value=object.

    :param groups: dict, list or tuple of GroupConfig objects. If dict: key=name, value=object.

    :param logger_config: LoggerConfig object. If it is not defined, it will create a LoggerConfig
    object with the default parameters.

    """

    def __init__(self, credentials=None, token=None, box_type=None, channels=None, groups=None,
                 logger_config=None):
        self.credentials = expand_path(self._get(credentials, default=DEFAULT_CRED_PATH))
        self.token = expand_path(self._get(token, default=DEFAULT_TOKEN_PATH))
        self.box_type = self._get(box_type, default=DEFAULT_BOX_TYPE)

        self.logger_config = self._get(logger_config, default=LoggerConfig())

        self.channels = self._parse_as_dict(channels)
        self.groups = self._parse_as_dict(groups)

    def _parse_as_dict(self, value):
        """
        Parse channels or groups as a dict with the format `name`: `entity` where `name` is the
        name of the channel or the group and `entity` is a ChannelConfig or GroupConfig object.

        It supports:
          - Explicit dict: {'ch1': channel1, 'ch2': channel2, ...}
          - List or tuple of config objects: [channel1, channel2, ...]

        """
        resolved = self._get(value, {})

        if isinstance(resolved, dict):
            return resolved
        elif isinstance(resolved, (list, tuple)):
            return {e.name: e for e in resolved}
        else:
            raise ValueError('{!r} must be a dict (name: config object) or an iterable of ' \
                'config objects'.format(value))

    def add_channel(self, channel):
        self.channels[channel.name] = channel

    def add_group(self, group):
        self.groups[group.name] = group

    def get_channels(self, names=None):
        """
        Get a filtered list of channels by channel name or group name.

        :param names: iterable of channel names or group names.

        """
        if not names:
            return self.channels.values()

        filtered = []
        for name in names:
            if name in self.channels:
                filtered.append(self.channels[name])
            elif name in self.groups:
                filtered.extend([self.channels[c] for c in self.groups[name].channels])
            else:
                raise ValueError('Channel {!r} is not present in config file'.format(name))
        return filtered