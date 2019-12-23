from mailbox import Maildir
from mailbox import mbox
from mailbox import MH
from mailbox import Babyl
from mailbox import MMDF
import os

from .message import MessageFormatter


class Mailbox:
    """
    Mailbox storage with state.
    """
    def __init__(self, box_type, path, formatter=None):
        self.path = path
        self.formatter = formatter
        if self.formatter is None:
            self.formatter = MessageFormatter()

        self.state_file = os.path.join(path, '.gmailsyncstate')
        self.state = self._load_state()

        if box_type == 'maildir':
            self.mailbox = Maildir(path)
        elif box_type == 'mbox':
            self.mailbox = mbox(path)
        elif box_type == 'mh':
            self.mailbox = MH(path)
        elif box_type == 'babyl':
            self.mailbox = Babyl(path)
        elif box_type == 'mmdf':
            self.mailbox = MMDF(path)
        else:
            raise NotImplementedError('Unsupported mailbox: {!r}'.format(box_type))

    def add(self, message):
        """
        Store a message in the mailbox.

        :param message: Gmail API message
        https://developers.google.com/gmail/api/v1/reference/users/messages#resource

        It must be a dict with at least two keys:
          - raw: the entire email message in an RFC 2822 formatted and base64url encoded string.
          - internalDate: the internal message creation timestamp (epoch ms), which determines
            ordering in the inbox. It is used to track the state of the mailbox.
          - labelIds: list of labels with which the message has been labeled.

        """
        formatted = self.formatter.format(message)
        self.mailbox.add(formatted['message'])
        self._update_state(formatted['timestamp'])

    def get_last_timestamp(self):
        return self.state

    def _update_state(self, timestamp):
        """
        Save the state of the already stored messages before to continue storing more messages
        to be able to recover the synchronization in case of failure.

        """
        if self.state is None:
            self.state = timestamp
        else:
            self.state = max(self.state, timestamp)
        self._save_state(self.state)

    def _load_state(self):
        if os.path.isfile(self.state_file):
            with open(self.state_file, 'r') as f:
                return int(f.read().strip())

    def _save_state(self, state):
        with open(self.state_file, 'w') as f:
            f.write(str(state))

    def __str__(self):
        return 'Mailbox <{}>'.format(self.path)
