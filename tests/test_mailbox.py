import unittest
from unittest.mock import Mock, MagicMock, patch
import contextlib
import os

from gmailsync.mailbox import Mailbox


TIMESTAMP = 1577060763


class MailBoxFactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.load_state_patcher = patch('gmailsync.mailbox.Mailbox._load_state')
        self.load_state_patcher.start()

    def tearDown(self):
        self.load_state_patcher.stop()

    @patch('gmailsync.mailbox.Maildir')
    def test_create_maildir_mailbox(self, mock_maildir):
        Mailbox('maildir', '/mail/box')
        mock_maildir.assert_called_with('/mail/box')

    @patch('gmailsync.mailbox.mbox')
    def test_create_mbox_mailbox(self, mock_mbox):
        Mailbox('mbox', '/mail/box')
        mock_mbox.assert_called_with('/mail/box')

    @patch('gmailsync.mailbox.MH')
    def test_create_mh_mailbox(self, mock_mh):
        Mailbox('mh', '/mail/box')
        mock_mh.assert_called_with('/mail/box')

    @patch('gmailsync.mailbox.Babyl')
    def test_create_babyl_mailbox(self, mock_babyl):
        Mailbox('babyl', '/mail/box')
        mock_babyl.assert_called_with('/mail/box')

    @patch('gmailsync.mailbox.MMDF')
    def test_create_mmdf_mailbox(self, mock_mmdf):
        Mailbox('mmdf', '/mail/box')
        mock_mmdf.assert_called_with('/mail/box')

    def test_invalid_box_type(self):
        with self.assertRaisesRegex(NotImplementedError, "Unsupported mailbox: 'invalid'"):
            Mailbox('invalid', '/mail/box')


class MailboxOperationsTestCase(unittest.TestCase):

    def setUp(self):
        self.maildir_patcher = patch('gmailsync.mailbox.Maildir')
        self.mock_maildir_class = self.maildir_patcher.start()
        self.mock_maildir = self.mock_maildir_class.return_value

        self.open_patcher = patch('gmailsync.mailbox.open')
        self.mock_open = self.open_patcher.start()

        self.isfile_patcher = patch('gmailsync.mailbox.os.path.isfile')
        self.mock_isfile = self.isfile_patcher.start()

    def tearDown(self):
        self.maildir_patcher.stop()
        self.open_patcher.stop()
        self.isfile_patcher.stop()

    def test_add_message(self):
        formatter = Mock()
        formatter.format.return_value = {'message': 'the message', 'timestamp': TIMESTAMP}

        mailbox = Mailbox('maildir', '/mail/box', formatter=formatter)
        mailbox.add('message_entity')

        formatter.format.assert_called_with('message_entity')
        self.mock_maildir.add.assert_called_with('the message')

    def test_update_state_after_adding_first_message(self):
        formatter = Mock()
        formatter.format.return_value = {'message': 'the message', 'timestamp': TIMESTAMP}

        mailbox = Mailbox('maildir', '/mail/box', formatter=formatter)

        with self._verify_state_saved('/mail/box', TIMESTAMP):
            mailbox.add('message_entity')
        self.assertEqual(mailbox.get_last_timestamp(), TIMESTAMP)

    def test_update_state_after_adding_a_more_recent_message(self):
        timestamp2 = TIMESTAMP + 100

        formatter = Mock()
        formatter.format.return_value = {'message': 'the message', 'timestamp': timestamp2}

        mailbox = Mailbox('maildir', '/mail/box', formatter=formatter)
        mailbox.state = TIMESTAMP

        with self._verify_state_saved('/mail/box', timestamp2):
            mailbox.add('message_entity')

        self.assertEqual(mailbox.get_last_timestamp(), timestamp2)

    def test_get_last_timestamp_from_state_file(self):
        mock_file = MagicMock()
        mock_file.read.return_value = str(TIMESTAMP)
        self.mock_open.return_value.__enter__.return_value = mock_file
        self.mock_isfile.return_value = True

        mailbox = Mailbox('maildir', '/mail/box')
        timestamp = mailbox.get_last_timestamp()

        self.assertEqual(timestamp, TIMESTAMP)
        self.mock_open.assert_called_once_with('/mail/box/.gmailsyncstate', 'r')
        mock_file.read.assert_called()

    def test_get_last_timestamp_if_state_file_does_not_exist(self):
        self.mock_isfile.return_value = False

        mailbox = Mailbox('maildir', '/mail/box')
        timestamp = mailbox.get_last_timestamp()

        self.assertIsNone(timestamp)
        self.mock_open.assert_not_called()

    def test_str(self):
        mailbox = Mailbox('maildir', '/mail/box')
        self.assertEqual('Mailbox </mail/box>', str(mailbox))

    @contextlib.contextmanager
    def _verify_state_saved(self, path, timestamp):
        state_path = os.path.join(path, '.gmailsyncstate')
        mock_file = MagicMock()
        self.mock_open.return_value.__enter__.return_value = mock_file
        yield
        self.mock_open.assert_called_with(state_path, 'w')
        mock_file.write.assert_called_once_with(str(timestamp))
