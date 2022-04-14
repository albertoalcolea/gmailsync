import unittest
from unittest.mock import patch, call

from gmailsync.config.models import Config, ChannelConfig
from gmailsync.channel import Channel, channel_factory


class ChannelTestCase(unittest.TestCase):

    @patch('gmailsync.channel.Mailbox')
    def test_channel_factory(self, mock_mailbox):
        ch1 = ChannelConfig(name='ch1', mailbox_path='/mail/ch1', box_type='maildir', query='label:STARRED')
        ch2 = ChannelConfig(name='ch2', mailbox_path='/mail/ch2', box_type='maildir', query='label:INBOX')
        ch3 = ChannelConfig(name='ch3', mailbox_path='/mail/ch3', box_type='mbox', query='other query')
        config = Config(channels=[ch1, ch2, ch3])

        channels_to_sync = ['ch1', 'ch3']

        channels = channel_factory(config, channels_to_sync)

        self.assertEqual(len(channels), 2)
        self._verify_channel(channels[0], 'ch1', 'label:STARRED')
        self._verify_channel(channels[1], 'ch3', 'other query')

        mock_mailbox.assert_has_calls([
            call('maildir', '/mail/ch1'),
            call('mbox', '/mail/ch3')
        ])

    @patch('gmailsync.channel.log')
    def test_create_channel_with_query_with_after(self, mock_log):
        channel = Channel('ch1', 'fake_mailbox', 'label:INBOX after:2018-05-01')
        self._verify_channel(channel, 'ch1', 'label:INBOX after:2018-05-01')
        mock_log.warn.assert_called_with("'after:' will be overwritten in query to do incremental queries based on the "
                                         "saved state")

    def _verify_channel(self, channel, name, query):
        self.assertTrue(isinstance(channel, Channel))
        self.assertEqual(channel.name, name)
        self.assertEqual(channel.query, query)
        self.assertIsNotNone(channel.mailbox)
