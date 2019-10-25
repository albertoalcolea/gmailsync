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

    def __init__(self, client, channels):
        self.client = client
        self.channels = channels

    def sync(self):
        # TODO: optimize routing for messages tagged with multiple labels
        for channel in self.channels:
            self.sync_channel(channel)

    def sync_channel(self, channel):
        last_timestamp = channel.mailbox.get_state()

        log.debug('Channel [%s] - Getting new messages', channel.name)
        msg_descs = self.client.list(query=channel.query, since=last_timestamp)
        msg_descs.reverse() # ASC order

        log.debug('Channel [%s] - Fetching %s new messages', channel.name, len(msg_descs))

        total = 0

        # Sending batches larger than 50 requests is not recommended.
        # https://developers.google.com/gmail/api/v1/reference/quota
        for chunk in chunked(msg_descs, 50):
            messages = self.client.fetch(chunk)
            for raw_msg in messages:
                msg = self._decode(raw_msg)
                channel.mailbox.add(msg)
                total += 1

            # Safe path to save the state of the already stored messages before to continue with
            # next chunk
            last_timestamp = self._get_last_timestamp(messages)
            channel.mailbox.save_state(last_timestamp)

            log.debug('Channel [%s] - %s new messages stored', channel.name, total)

        log.info('Channel [%s] - %s new messages synchronized', channel.name, total)

    def _decode(self, message):
        return base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    def _get_last_timestamp(self, messages):
        return int(messages[-1]['internalDate']) // 1000 # seconds since epoch, discarding millis
