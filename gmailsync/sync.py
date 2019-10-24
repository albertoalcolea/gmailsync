import base64
import itertools
import logging


log = logging.getLogger('gmailsync')


def chunked(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk


class Synchronizer:

    def __init__(self, client, mailboxes):
        self.client = client
        self.mailboxes = mailboxes

    def sync(self):
        # TODO: optimize routing for messages tagged with multiple labels
        for label, mailbox in self.mailboxes.items():
            self.sync_mailbox(label, mailbox)


    def sync_mailbox(self, label, mailbox):
        last_timestamp = mailbox.get_state()

        log.debug('Getting new messages for remote [%s]', label)
        msg_descs = self.client.list(label=label, since=last_timestamp)
        msg_descs.reverse() # ASC order

        log.debug('Fetching messages for remote [%s]', label)

        total = 0

        # Sending batches larger than 50 requests is not recommended.
        # https://developers.google.com/gmail/api/v1/reference/quota
        for chunk in chunked(msg_descs, 50):
            messages = self.client.fetch(chunk)
            for raw_msg in messages:
                msg = self._decode(raw_msg)
                mailbox.add(msg)
                total += 1

            # Safe path to save the state of the already stored messages before to continue with
            # next chunk
            last_timestamp = self._get_last_timestamp(messages)
            mailbox.save_state(last_timestamp)

            log.debug('Stored %s new messages for remote [%s]', total, label)

        log.info('Synchronized %s new messages for remote [%s]', total, label)

    def _decode(self, message):
        return base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    def _get_last_timestamp(self, messages):
        return int(messages[-1]['internalDate']) // 1000 # seconds since epoch, discarding millis
