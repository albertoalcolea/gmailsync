import unittest

from gmailsync.config.validator import ConfigValidator, ConfigurationError
from gmailsync.config.models import Config, ChannelConfig, GroupConfig


class ConfigValidationTestCase(unittest.TestCase):

    def setUp(self):
        self.validator = ConfigValidator()

    def test_valid(self):
        channel1 = ChannelConfig(name='ch1', mailbox_path='/var/mail/ch1', query='label:ch1')
        group1 = GroupConfig(name='gr1', channels=['ch1'])
        config = Config(channels={'ch1': channel1}, groups={'gr1': group1})
        self.validator.validate(config)

    def test_no_channels(self):
        config = Config()
        with self.assertRaisesRegex(ConfigurationError, 'No channels found in config'):
            self.validator.validate(config)

    def test_invalid_channels_in_group(self):
        channel1 = ChannelConfig(name='ch1', mailbox_path='/var/mail/ch1', query='label:ch1')
        group1 = GroupConfig(name='gr1', channels=['other'])
        config = Config(channels={'ch1': channel1}, groups={'gr1': group1})
        with self.assertRaisesRegex(ConfigurationError, "Channel 'other' in group 'gr1' is not defined"):
            self.validator.validate(config)
