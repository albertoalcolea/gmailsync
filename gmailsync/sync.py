import logging
import secrets
import time

from .utils import chunked


log = logging.getLogger('gmailsync')


# Sending batches larger than 50 requests is not recommended.
# https://developers.google.com/gmail/api/v1/reference/quota
# however, quota limits translate to about max 12 messages.get()
# requests per second, so we play safe with 10.
# https://developers.google.com/workspace/gmail/api/reference/quota
CHUNK_SIZE = 10


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

        time.sleep(1)  # avoid rate limit

        total = 0

        for chunk in chunked(msg_descs, CHUNK_SIZE):
            # Retry loop for 429 'Too Many Requests'
            retries = 0
            max_retries = 5
            while retries < max_retries:
                try:
                    log.debug('Fetching %s messages', len(chunk))
                    messages = self.client.fetch(chunk)
                    for message in messages:
                        channel.mailbox.add(message)
                        total += 1
                    break
                except Exception:
                    retries += 1
                    # Exponential Backoff with Jitter
                    delay = (2**retries) + secrets.SystemRandom().uniform(0, 1)
                    log.warning(f'Rate limit exceeded. Retrying in {delay:.2f} seconds... ({retries}/{max_retries})')
                    time.sleep(delay)
            # Throttle between chunks to maintain a safe per-second quota
            time.sleep(1)

            log.debug('Channel [%s] - %s new messages stored', channel.name, total)

        log.info('Channel [%s] - %s new messages synchronized', channel.name, total)
