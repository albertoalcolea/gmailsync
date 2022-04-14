import unittest

from gmailsync.config.models import Config, ChannelConfig, GroupConfig


CH1 = ChannelConfig(name='ch1', mailbox_path='~/mail/ch1', query='label:ch1')
CH2 = ChannelConfig(name='ch2', mailbox_path='~/mail/ch2', query='label:ch2')
CH3 = ChannelConfig(name='ch3', mailbox_path='~/mail/ch3', query='label:ch3')
GR1 = GroupConfig(name='gr1', channels=['ch1', 'ch2'])
GR2 = GroupConfig(name='gr2', channels=['ch3'])


class ConfigConstructorConversionsTestCase(unittest.TestCase):

    def test_channels_from_dict(self):
        config = Config(channels={'ch1': CH1, 'ch2': CH2})
        self.assertEqual(config.channels, {'ch1': CH1, 'ch2': CH2})

    def test_channels_from_tuple(self):
        config = Config(channels=(CH1, CH2))
        self.assertEqual(config.channels, {'ch1': CH1, 'ch2': CH2})

    def test_channels_from_list(self):
        config = Config(channels=[CH1, CH2])
        self.assertEqual(config.channels, {'ch1': CH1, 'ch2': CH2})

    def test_invalid_channels(self):
        with self.assertRaises(ValueError):
            Config(channels='invalid')

    def test_groups_from_dict(self):
        config = Config(groups={'gr1': GR1, 'gr2': GR2})
        self.assertEqual(config.groups, {'gr1': GR1, 'gr2': GR2})

    def test_groups_from_tuple(self):
        config = Config(groups=(GR1, GR2))
        self.assertEqual(config.groups, {'gr1': GR1, 'gr2': GR2})

    def test_groups_from_list(self):
        config = Config(groups=[GR1, GR2])
        self.assertEqual(config.groups, {'gr1': GR1, 'gr2': GR2})

    def test_invalid_groups(self):
        with self.assertRaises(ValueError):
            Config(groups='invalid')


class ConfigFilterTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config(channels={'ch1': CH1, 'ch2': CH2, 'ch3': CH3}, groups={'gr1': GR1})

    def test_no_filter(self):
        channels = self.config.get_channels()
        self._verify_eq_channels(channels, ['ch1', 'ch2', 'ch3'])

    def test_none_filter(self):
        channels = self.config.get_channels(names=None)
        self._verify_eq_channels(channels, ['ch1', 'ch2', 'ch3'])

    def test_empty_filter(self):
        channels = self.config.get_channels(names=[])
        self._verify_eq_channels(channels, ['ch1', 'ch2', 'ch3'])

    def test_valid_channel_filter(self):
        channels = self.config.get_channels(names=['ch1', 'ch3'])
        self._verify_eq_channels(channels, ['ch1', 'ch3'])

    def test_valid_group_filter(self):
        channels = self.config.get_channels(names=['gr1'])
        self._verify_eq_channels(channels, ['ch1', 'ch2'])

    def test_valid_channel_and_group_filter(self):
        channels = self.config.get_channels(names=['gr1', 'ch3'])
        self._verify_eq_channels(channels, ['ch1', 'ch2', 'ch3'])

    def test_invalid_filter(self):
        with self.assertRaisesRegex(ValueError, "Channel 'INVALID' is not present in config file"):
            self.config.get_channels(names=['INVALID'])

    def _verify_eq_channels(self, channels, expected_names):
        channel_names = [c.name for c in channels]
        self.assertEqual(channel_names, expected_names)
