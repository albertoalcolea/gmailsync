import unittest
from unittest.mock import Mock, patch, call

from gmailsync.sync import Synchronizer
from gmailsync.channel import Channel


CHANNEL1_NAME = 'channel1'
QUERY1 = 'query1'
TIMESTAMP1 = 'timestamp1'

CHANNEL2_NAME = 'channel2'
QUERY2 = 'query2'
TIMESTAMP2 = 'timestamp1'


class SynchronizerTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Mock()

        self.mailbox1 = Mock()
        self.mailbox1.get_last_timestamp.return_value = TIMESTAMP1
        self.channel1 = Channel(CHANNEL1_NAME, self.mailbox1, QUERY1)

        self.mailbox2 = Mock()
        self.mailbox2.get_last_timestamp.return_value = TIMESTAMP2
        self.channel2 = Channel(CHANNEL2_NAME, self.mailbox2, QUERY2)

    def test_sync_one_channel(self):
        self.client.list.return_value = ['msg_id1', 'msg_id2', 'msg_id3']
        self.client.fetch.return_value = ['msg3', 'msg2', 'msg1']

        synchronizer = Synchronizer(self.client, [self.channel1])
        synchronizer.sync()

        self.client.list.assert_called_with(query=QUERY1, since=TIMESTAMP1)
        self.client.fetch.assert_called_with(('msg_id3', 'msg_id2', 'msg_id1'))
        self.mailbox1.add.assert_has_calls([call('msg3'), call('msg2'), call('msg1')])

    def test_sync_multiple_mailboxes(self):
        self.client.list.side_effect = [['msg_id1', 'msg_id2', 'msg_id3'], ['msg_id4', 'msg_id5']]
        self.client.fetch.side_effect = [['msg3', 'msg2', 'msg1'], ['msg5', 'msg4']]

        synchronizer = Synchronizer(self.client, [self.channel1, self.channel2])
        synchronizer.sync()

        self.client.list.assert_has_calls([call(query=QUERY1, since=TIMESTAMP1), call(query=QUERY2, since=TIMESTAMP2)])
        self.client.fetch.assert_has_calls([call(('msg_id3', 'msg_id2', 'msg_id1')), call(('msg_id5', 'msg_id4'))])
        self.mailbox1.add.assert_has_calls([call('msg3'), call('msg2'), call('msg1')])
        self.mailbox2.add.assert_has_calls([call('msg5'), call('msg4')])

    @patch('gmailsync.sync.CHUNK_SIZE', 2)
    def test_fetch_messages_in_chunks(self):
        self.client.list.return_value = ['msg_id1', 'msg_id2', 'msg_id3']
        self.client.fetch.side_effect = [['msg3', 'msg2'], ['msg1']]

        synchronizer = Synchronizer(self.client, [self.channel1])
        synchronizer.sync()

        self.client.list.assert_called_with(query=QUERY1, since=TIMESTAMP1)
        self.client.fetch.assert_has_calls([call(('msg_id3', 'msg_id2')), call(('msg_id1',))])
        self.mailbox1.add.assert_has_calls([call('msg3'), call('msg2'), call('msg1')])
