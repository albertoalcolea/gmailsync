from .sync import Synchronizer
from .client import Client
from .mailbox import Mailbox
from .channel import Channel


__title__ = 'gmailsync'
__version__ = '0.1.0'
__author__ = 'Alberto Alcolea'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2019 Alberto Alcolea'

__all__ = [
    'Synchronizer', 'Client', 'Mailbox', 'Channel'
]
