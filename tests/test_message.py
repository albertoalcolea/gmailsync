import unittest
from unittest.mock import patch
import base64
import datetime

from gmailsync.message import MessageFormatter


MAIL_MESSAGE = b'From: John Doe <jdoe@machine.example>\r\n' \
               b'Sender: Michael Jones <mjones@machine.example>\r\n' \
               b'To: Mary Smith <mary@example.net>\r\n' \
               b'Subject: Saying Hello\r\n' \
               b'Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n' \
               b'Message-ID: <1234@local.machine.example>\r\n' \
               b'\r\n' \
               b'This is a message just to say hello. So, "Hello".'

DATE = datetime.datetime(1997, 11, 21, 9, 55, 6)
TIMESTAMP = int(DATE.timestamp())


class MessageFormatterTestCase(unittest.TestCase):

    def setUp(self):
        self.formatter = MessageFormatter()
        self.maxDiff = None # To see full diff in case of error

    def test_format_actual_mail_message(self):
        message = self._create_message(MAIL_MESSAGE, DATE)
        formatted = self.formatter.format(message)
        expected = {'message': MAIL_MESSAGE, 'timestamp': TIMESTAMP}
        self.assertEqual(formatted, expected)

    def _create_message(self, mail_message, date, labels=None):
        if labels is None:
            labels = []
        return {
            'raw': base64.urlsafe_b64encode(mail_message).decode('ASCII'),
            'internalDate': str(int(date.timestamp()) * 1000),
            'labelIds': labels,
        }