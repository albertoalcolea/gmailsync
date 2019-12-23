import logging

from .mailbox import Mailbox


log = logging.getLogger('gmailsync')


def channel_factory(config, channels_to_sync):
    """
    Create Channel objects from configurations.

    This factory instantiate and configure a list of Channel objects as well as the Mailbox
    objects for each channel.

    :param config: Config object with the configuration of the application.

    :param channels_to_sync: list of channel names or group names to synchronize

    """
    channels = []
    for channel_config in config.get_channels(channels_to_sync):
        if channel_config.box_type is None:
            # Default box_type
            box_type = config.box_type
        else:
            # Channel explicit box-type
            box_type = channel_config.box_type
        mailbox = Mailbox(box_type, channel_config.mailbox_path)
        channel = Channel(channel_config.name, mailbox, channel_config.query)
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
        return 'Channel <{}>'.format(self.name)
