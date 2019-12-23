import email
from email import policy
import base64
import datetime


class MessageFormatter:
    """
    Fixer to format malformed messages according to the RFC 2822 specification:
    https://tools.ietf.org/html/rfc2822

    Actual mail messages should be well-formed.


    GTalk
    -----
    Some old messages from GTalk contains some mandatory fields in the header section but others
    like `date` are missing.

    Each message contains in the body the entire conversation:
    https://developers.google.com/talk/

    Example:
    ```
    Delivered-To: alice@gmail.com
    Received: by 10.112.87.7 with SMTP id s5n3asdfdaf3c;        Wed, 7 Mar 2012 11:36:25 -0800 (PST)
    Received: by 10.42.117.6 with SMTP id mgfsdjkjhr43w;        Wed, 07 Mar 2012 11:36:24 -0800 (PST)
    From: Bob Smith <bob@gmail.com>
    To: alice@gmail.com
    Message-ID: <1234567.1234567.112233445566.chat@gmail.com>
    MIME-Version: 1.0
    Content-Type: multipart/alternative; boundary="----=_Part_2020123_6002233.112233445566"
    Subject: Chat with Bob Smith

    ------=_Part_2020123_6002233.112233445566
    Content-Type: text/xml; charset=utf-8
    Content-Transfer-Encoding: 7bit


    <con:conversation xmlns:con="google:archive:conversation">
      (...)
    </con:conversation>
    ```

    Note: it may contain another part with the HTML representation of the conversation


    Hangouts
    --------

    Messages from Hangouts and Google Chat just contain the `from` field.
    Each Gmail message contains a single real message, not the entire conversation.

    Example:
    ```
    From: Bob Smith <bob@gmail.com>


    Hey! How are you?
    ```

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
          - labelIds: list of labels with which the message has been labeled.

        """
        message = self._decode(message_entity)
        timestamp = self._get_timestamp(message_entity)

        if 'CHAT' in message_entity['labelIds']:
            message = self._fix_message(message, timestamp)

        return {'message': message, 'timestamp': timestamp}

    def _decode(self, message):
        return base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    def _get_timestamp(self, message):
        return int(message['internalDate']) // 1000 # seconds since epoch, discarding millis

    def _fix_message(self, malformed_message, timestamp):
        message = self.parser.parsestr(malformed_message.decode('UTF-8'))

        if 'Date' not in message:
            dt = datetime.datetime.fromtimestamp(timestamp)
            message['Date'] = email.utils.format_datetime(dt)

        if 'Message-ID' not in message:
            message['Message-ID'] = email.utils.make_msgid(idstring='gmailsync-fix', domain='gmail.com')

        return message.as_string(policy=policy.SMTP).encode('UTF-8')