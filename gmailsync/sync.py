import logging

from .utils import chunked


log = logging.getLogger('gmailsync')


# Sending batches larger than 50 requests is not recommended.
# https://developers.google.com/gmail/api/v1/reference/quota
CHUNK_SIZE = 50


class Synchronizer:

    def __init__(self, client, channels):
        self.client = client
        self.channels = channels

    def sync(self):
        # TODO: optimize routing for messages tagged with multiple labels
        for channel in self.channels:
            self.sync_channel(channel)

    def sync_channel(self, channel):
        last_timestamp = channel.mailbox.get_last_timestamp()

        log.debug('Channel [%s] - Getting new messages', channel.name)
        msg_descs = self.client.list(query=channel.query, since=last_timestamp)
        msg_descs.reverse()  # ASC order, oldest first

        log.debug('Channel [%s] - Fetching %s new messages', channel.name, len(msg_descs))

        total = 0

        for chunk in chunked(msg_descs, CHUNK_SIZE):
            messages = self.client.fetch(chunk)
            for message in messages:
                channel.mailbox.add(message)
                total += 1

            log.debug('Channel [%s] - %s new messages stored', channel.name, total)

        log.info('Channel [%s] - %s new messages synchronized', channel.name, total)
