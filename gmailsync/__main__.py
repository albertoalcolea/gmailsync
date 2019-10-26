import sys
import argparse
import traceback
import logging

from .config import ConfigReader, set_up_logger
from .client import Client
from .sync import Synchronizer
from .channel import channel_factory
from .cli import cprint


log = logging.getLogger('gmailsync')


def load_args():
    parser = argparse.ArgumentParser(description='gmailsync. Synchronize and save a backup of your gmail messages')
    parser.add_argument('-c', '--conf', help='Configuration file', metavar='file', default='~/.gmailsync.conf')
    parser.add_argument('-l', '--labels', help='List the available labels', action='store_true')
    parser.add_argument('-v', '--verbose', help='Show debug log messages in the log', action='store_true')
    parser.add_argument('channels', help='Channel name or group name to synchronize. If none defined it will synchronize all of them', nargs='*')
    return parser.parse_args()


def list_labels(client):
    labels = client.labels()
    system_labels = [label['name'] for label in labels if label['type'] == 'system']
    user_labels = [label['name'] for label in labels if label['type'] == 'user']
    print('List of labels:')
    for label in sorted(system_labels):
        print('  ', label)
    for label in sorted(user_labels):
        print('  ', label)


def sync_mailboxes(client, channels_to_sync):
    channels = channel_factory(channels_to_sync)
    synchronizer = Synchronizer(client, channels)
    synchronizer.sync()


def main():
    args = load_args()

    try:
        config_reader = ConfigReader()
        config = config_reader.load_config(args.conf)

        set_up_logger(args.verbose, config.logger_config)

        client = Client(config.credentials, config.token)

        if args.labels:
            list_labels(client)
        else:
            channels_to_sync = config.get_channels(args.channels)
            sync_mailboxes(client, channels_to_sync)

    except (KeyboardInterrupt, SystemExit):
        # Do nothing
        pass

    except Exception as e:
        if log.handlers:
            # If logger is already configured
            log.error('Something went wrong', exc_info=True)

        cprint(e, status='error', file=sys.stderr)
        if args.verbose:
            traceback.print_exc(file=sys.stderr)

        sys.exit(1)


if __name__ == '__main__':
    main()
