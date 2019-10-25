from mailbox import Maildir
from mailbox import mbox
from mailbox import MH
from mailbox import Babyl
from mailbox import MMDF
import os


class Mailbox:
    """
    Mailbox storage with state.
    """
    def __init__(self, box_type, path):
        self.path = path
        self.state_file = os.path.join(path, '.gmailsyncstate')

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
            raise NotImplementedError('Mailbox not implemented')

    def add(self, message):
        """
        Store a message in the mailbox.
        :param messagge: must be a RFC 2822-compliant message as a string or a byte string.
        """
        self.mailbox.add(message)

    def save_state(self, last_timestamp):
        with open(self.state_file, 'w') as f:
            f.write(str(last_timestamp))

    def get_state(self):
        if os.path.isfile(self.state_file):
            with open(self.state_file) as f:
                return int(f.read().strip())

    def __str__(self):
        return 'Mailbox <{}>'.format(self.path)