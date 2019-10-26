import logging
from .mailbox import Mailbox


log = logging.getLogger('gmailsync')


def channel_factory(channels_config):
    """
    Create Channel objects from ChannelConfig configurations.

    This factory instantiate and configure a list of Channel objects as well as the Mailbox
    objects for each channel.

    :param channels_config: list of ChannelConfig objects with the configuration of each channel.

    """
    channels = []
    for config in channels_config:
        mailbox = Mailbox(config.box_type, config.mailbox_path)
        channel = Channel(config.name, mailbox, config.query)
        channels.append(channel)
    return channels


class Channel:

    def __init__(self, name, mailbox, query):
        self.name = name
        self.mailbox = mailbox
        self.query = query

        if 'after:' in query:
            log.warn("'after:' will be overwritten in query to do incremental queries based on the saved state")

    def __str__(self):
        return self.name