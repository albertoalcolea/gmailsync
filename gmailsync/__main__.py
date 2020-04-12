import sys
import argparse
import traceback
import logging

from .config import load_config, set_up_logger, DEFAULT_CONF_PATH
from .client import Client
from .sync import Synchronizer
from .channel import channel_factory
from .cli import Status, cprint


log = logging.getLogger('gmailsync')


def load_args():
    parser = argparse.ArgumentParser(description='gmailsync. Synchronize and save a backup of your gmail messages')
    parser.add_argument('-c', '--conf', help='Configuration file', metavar='file', default=DEFAULT_CONF_PATH)
    parser.add_argument('-l', '--labels', help='List the available labels', action='store_true')
    parser.add_argument('-v', '--verbose', help='Show debug log messages in the log', action='store_true')
    parser.add_argument('channels', help='List of channel names or group names to synchronize. If none defined it will synchronize all channels', nargs='*')
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


def sync_mailboxes(config, client, channels_to_sync):
    channels = channel_factory(config, channels_to_sync)
    synchronizer = Synchronizer(client, channels)
    synchronizer.sync()


def main():
    args = load_args()

    try:
        config = load_config(args.conf)

        set_up_logger(args.verbose, config.logger_config)

        client = Client(config.credentials, config.token)

        if args.labels:
            list_labels(client)
        else:
            sync_mailboxes(config, client, args.channels)

    except (KeyboardInterrupt, SystemExit):
        # Do nothing
        pass

    except Exception as e:
        if log.handlers:
            # If logger is already configured
            log.error('Something went wrong', exc_info=True)
        elif args.verbose:
            traceback.print_exc(file=sys.stderr)
        cprint(e, status=Status.ERROR, file=sys.stderr)

        sys.exit(1)


if __name__ == '__main__':
    main()
