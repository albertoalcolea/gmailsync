import email
from email import policy
import base64
import datetime


class MessageFormatter:
    """
    Fixer to format malformed messages according to the RFC 2822 specification:
    https://tools.ietf.org/html/rfc2822

    Actual mail messages should be well-formed.

    """
    def __init__(self):
        self.parser = email.parser.HeaderParser()

    def format(self, message_entity):
        """
        Format a message according to the RFC 2822 specification and try to fix malformed
        messages.

        :param message: Gmail API message
        https://developers.google.com/gmail/api/v1/reference/users/messages#resource

        It must be a dict with at least three keys:
          - raw: the entire email message in an RFC 2822 formatted and base64url encoded string.
          - internalDate: the internal message creation timestamp (epoch ms), which determines
            ordering in the inbox. It is used to track the state of the mailbox.

        """
        message = self._decode(message_entity)
        timestamp = self._get_timestamp(message_entity)
        return {'message': message, 'timestamp': timestamp}

    def _decode(self, message):
        return base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    def _get_timestamp(self, message):
        return int(message['internalDate']) // 1000 # seconds since epoch, discarding millis