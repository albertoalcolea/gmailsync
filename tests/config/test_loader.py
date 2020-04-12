import unittest
from unittest.mock import patch

from gmailsync.config.parser import EnhancedConfigParser, NoSectionError, NoOptionError, _UNSET
from gmailsync.config.loader import ConfigLoader
from gmailsync.config.validator import ConfigurationError


class FakeParser:
    """
    Fake parser that bypass the content of a dict without any extra processing.

    """

    def __init__(self, config):
        self.config = config

    def sections(self):
        return self.config.keys()

    def __getattr__(self, attr):
        if attr.startswith('get'):
            return self._fakeget
        else:
            return super().__getattr__(attr)

    def _fakeget(self, section, option, fallback=_UNSET, **kwargs):
        if section in self.config and option in self.config[section]:
            return self.config[section][option]
        else:
            if fallback == _UNSET:
                if section not in self.config:
                    raise NoSectionError(section)
                else:
                    raise NoOptionError(option, section)
            else:
                return fallback


class ConfigLoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.expand_path_patcher = patch('gmailsync.config.models.expand_path')
        self.mock_expand_path = self.expand_path_patcher.start()
        self.mock_expand_path.side_effect = lambda path : path

    def tearDown(self):
        self.expand_path_patcher.stop()

    def test_load_general_config(self):
        parser = FakeParser({
            'general': {
                'credentials': '/etc/gmailsync/credentials.json',
                'token': '/etc/gmailsync/token.pickle',
                'box_type': 'mbox'
            }
        })
        loader = ConfigLoader(parser)
        config = loader.load()
        self.assertEqual(config.credentials, '/etc/gmailsync/credentials.json')
        self.assertEqual(config.token, '/etc/gmailsync/token.pickle')
        self.assertEqual(config.box_type, 'mbox')

    def test_load_default_general_config(self):
        parser = FakeParser(dict())
        loader = ConfigLoader(parser)
        config = loader.load()
        self.assertEqual(config.credentials, '~/.gmailsync/credentials.json')
        self.assertEqual(config.token, '~/.gmailsync/token.pickle')
        self.assertEqual(config.box_type, 'maildir')

    def test_load_channels_config(self):
        parser = FakeParser({
            'channel-ch1': {
                'mailbox': '~/mail/ch1',
                'query': 'label:ch1',
                'box_type': 'mbox'
            },
            'channel-ch2': {
                'mailbox': '/var/mail/ch2',
                'query': 'label:ch2',
            },
        })
        loader = ConfigLoader(parser)
        config = loader.load()
        self.assertEqual(len(config.channels), 2)
        self.assertTrue('ch1' in config.channels)
        self.assertTrue('ch2' in config.channels)
        self._verify_channel(config.channels['ch1'], 'ch1', '~/mail/ch1', 'label:ch1', 'mbox')
        self._verify_channel(config.channels['ch2'], 'ch2', '/var/mail/ch2', 'label:ch2', None)

    def test_load_groups_config(self):
        parser = FakeParser({
            'group-gr1': {
                'channels': ['ch1', 'ch2']
            },
            'group-gr2': {
                'channels': ['ch3']
            }
        })
        loader = ConfigLoader(parser)
        config = loader.load()
        self.assertEqual(len(config.groups), 2)
        self.assertTrue('gr1' in config.groups)
        self.assertTrue('gr2' in config.groups)
        self._verify_group(config.groups['gr1'], 'gr1', ['ch1', 'ch2'])
        self._verify_group(config.groups['gr2'], 'gr2', ['ch3'])

    def test_load_logger_config(self):
        parser = FakeParser({
            'log': {
                'file': '/var/log/gmailsync.log',
                'file_max_bytes': 100,
                'file_backup_count': 3,
                'format': '%(message)s'
            }
        })
        loader = ConfigLoader(parser)
        config = loader.load()
        self.assertEqual(config.logger_config.file, '/var/log/gmailsync.log')
        self.assertEqual(config.logger_config.max_bytes, 100)
        self.assertEqual(config.logger_config.backup_count, 3)
        self.assertEqual(config.logger_config.format, '%(message)s')

    def test_load_default_logger_config(self):
        parser = FakeParser(dict())
        loader = ConfigLoader(parser)
        config = loader.load()
        self.assertEqual(config.logger_config.file, None)
        self.assertEqual(config.logger_config.max_bytes, 104857600)
        self.assertEqual(config.logger_config.backup_count, 50)
        self.assertEqual(config.logger_config.format, '%(asctime)s %(levelname)s [%(name)s] %(message)s')

    def test_no_option(self):
        parser = FakeParser({
             'channel-ch1': {
                'box_type': 'mbox'
            }
        })
        loader = ConfigLoader(parser)
        with self.assertRaisesRegex(ConfigurationError, "No option 'mailbox' in section: 'channel-ch1'"):
            config = loader.load()

    def test_invalid_section(self):
        parser = FakeParser({
            'this-is-not-valid': {
                'foo': 'bar'
            }
        })
        loader = ConfigLoader(parser)
        with self.assertRaisesRegex(ConfigurationError, "Invalid section name: 'this-is-not-valid'"):
            config = loader.load()

    def _verify_channel(self, channel, name, mailbox, query, box_type):
        self.assertEqual(channel.name, name)
        self.assertEqual(channel.mailbox_path, mailbox)
        self.assertEqual(channel.query, query)
        self.assertEqual(channel.box_type, box_type)

    def _verify_group(self, group, name, channels):
        self.assertEqual(group.name, name)
        self.assertEqual(group.channels, channels)
