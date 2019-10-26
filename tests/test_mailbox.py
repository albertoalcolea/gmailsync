import unittest
from unittest.mock import MagicMock, patch
import datetime

from gmailsync.mailbox import Mailbox


MAIL_MESSAGE = '''From: John Doe <jdoe@machine.example>
Sender: Michael Jones <mjones@machine.example>
To: Mary Smith <mary@example.net>
Subject: Saying Hello
Date: Fri, 21 Nov 1997 09:55:06 -0600
Message-ID: <1234@local.machine.example>

This is a message just to say hello.
So, "Hello".'''

TIMESTAMP = int(datetime.datetime(1997, 11, 21, 9, 55, 6).timestamp())
STR_TIMESTAMP = '880102506' # == str(TIMESTAMP)


class MailBoxFactoryTestCase(unittest.TestCase):

    @patch('gmailsync.mailbox.Maildir')
    def test_create_maildir_mailbox(self, mock_maildir):
        mailbox = Mailbox('maildir', '/mail/box')
        mock_maildir.assert_called_with('/mail/box')

    @patch('gmailsync.mailbox.mbox')
    def test_create_mbox_mailbox(self, mock_mbox):
        mailbox = Mailbox('mbox', '/mail/box')
        mock_mbox.assert_called_with('/mail/box')

    @patch('gmailsync.mailbox.MH')
    def test_create_mh_mailbox(self, mock_mh):
        mailbox = Mailbox('mh', '/mail/box')
        mock_mh.assert_called_with('/mail/box')

    @patch('gmailsync.mailbox.Babyl')
    def test_create_babyl_mailbox(self, mock_babyl):
        mailbox = Mailbox('babyl', '/mail/box')
        mock_babyl.assert_called_with('/mail/box')

    @patch('gmailsync.mailbox.MMDF')
    def test_create_mmdf_mailbox(self, mock_mmdf):
        mailbox = Mailbox('mmdf', '/mail/box')
        mock_mmdf.assert_called_with('/mail/box')


class MailboxOperationsTestCase(unittest.TestCase):

    def setUp(self):
        self.maildir_patcher = patch('gmailsync.mailbox.Maildir')
        self.mock_maildir_class = self.maildir_patcher.start()
        self.mock_maildir = self.mock_maildir_class.return_value

    def tearDown(self):
        self.maildir_patcher.stop()

    def test_invalid_box_type(self):
        with self.assertRaisesRegex(NotImplementedError, 'Unsupported mailbox'):
            Mailbox('unsupported mailbox', '/mail/box')

    def test_add_message(self):
        mailbox = Mailbox('maildir', '/mail/box')
        mailbox.add(MAIL_MESSAGE)
        self.mock_maildir.add.assert_called_with(MAIL_MESSAGE)

    @patch('gmailsync.mailbox.open')
    def test_save_state(self, mock_open):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        mailbox = Mailbox('maildir', '/mail/box')
        mailbox.save_state(TIMESTAMP)

        mock_open.assert_called_once_with('/mail/box/.gmailsyncstate', 'w')
        mock_file.write.assert_called_once_with(STR_TIMESTAMP)

    @patch('gmailsync.mailbox.open')
    @patch('gmailsync.mailbox.os.path.isfile')
    def test_get_state(self, mock_isfile, mock_open):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = STR_TIMESTAMP
        mock_isfile.return_value = True

        mailbox = Mailbox('maildir', '/mail/box')
        state = mailbox.get_state()

        self.assertEqual(state, TIMESTAMP)
        mock_open.assert_called_once_with('/mail/box/.gmailsyncstate', 'r')
        mock_file.read.assert_called()

    @patch('gmailsync.mailbox.open')
    @patch('gmailsync.mailbox.os.path.isfile')
    def test_get_state_if_state_file_does_not_exist(self, mock_isfile, mock_open):
        mock_isfile.return_value = False

        mailbox = Mailbox('maildir', '/mail/box')
        state = mailbox.get_state()

        self.assertIsNone(state)
        mock_open.assert_not_called()

    def test_str(self):
        mailbox = Mailbox('maildir', '/mail/box')
        self.assertEqual('Mailbox </mail/box>', str(mailbox))