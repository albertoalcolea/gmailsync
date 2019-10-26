import unittest
from unittest.mock import patch, call

from gmailsync.config import ChannelConfig
from gmailsync.channel import Channel, channel_factory
from gmailsync.mailbox import Mailbox


class ChannelTestCase(unittest.TestCase):

    @patch('gmailsync.channel.Mailbox')
    def test_channel_factory(self, mock_mailbox):
        ch_conf1 = self._create_channel_config(name='ch1', mailbox_path='/mail/ch1', box_type='maildir', query='label:STARRED')
        ch_conf2 = self._create_channel_config(name='ch2', mailbox_path='/mail/ch2', box_type='maildir', query='label:INBOX')
        ch_conf3 = self._create_channel_config(name='ch3', mailbox_path='/mail/ch3', box_type='mbox', query='other query')

        channels_config = [ch_conf1, ch_conf2, ch_conf3]

        channels = channel_factory(channels_config)

        self.assertEqual(len(channels), 3)
        self._verify_channel(channels[0], 'ch1', 'label:STARRED')
        self._verify_channel(channels[1], 'ch2', 'label:INBOX')
        self._verify_channel(channels[2], 'ch3', 'other query')

        mock_mailbox.assert_has_calls([
            call('maildir', '/mail/ch1'),
            call('maildir', '/mail/ch2'),
            call('mbox', '/mail/ch3')
        ])

    @patch('gmailsync.channel.log')
    def test_create_channel_with_query_with_after(self, mock_log):
        channel = Channel('ch1', 'fake_mailbox', 'label:INBOX after:2018-05-01')
        self._verify_channel(channel, 'ch1', 'label:INBOX after:2018-05-01')
        mock_log.warn.assert_called()

    def _create_channel_config(self, name, mailbox_path, box_type, query):
        config = ChannelConfig()
        config.name = name
        config.mailbox_path = mailbox_path
        config.box_type = box_type
        config.query = query
        return config

    def _verify_channel(self, channel, name, query):
        self.assertTrue(isinstance(channel, Channel))
        self.assertEqual(channel.name, name)
        self.assertEqual(channel.query, query)
        self.assertIsNotNone(channel.mailbox)