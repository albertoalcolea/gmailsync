# gmailsync

[![Build Status](https://travis-ci.org/albertoalcolea/gmailsync.svg?branch=master)](https://travis-ci.org/albertoalcolea/gmailsync)
[![Latest PyPI Version](https://img.shields.io/pypi/v/gmailsync.svg)](https://pypi.python.org/pypi/gmailsync)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/gmailsync.svg)](https://pypi.python.org/pypi/gmailsync)

Synchronize and save a backup of your Gmail messages

## Requirements

- python (3.6+)
- pip

## Installation
On all systems, install *gmailsync* by using `pip`:

```bash
pip install gmailsync
```

## Updating

```bash
pip install gmailsync --upgrade
```

## Usage

List Gmail labels:

```bash
gmailsync -l
```

Synchronize all channels:

```bash
gmailsync
```

Synchronize concrete channels/groups:

```bash
gmailsync group1 group2 channelXYZ
```

## Create a new Google Cloud Project
Gmailsync uses the Google API to retrieve messages from Gmail.

As it is a limited service unless your pay, gmailsync does not provide a common project, but you must create your own.

The free tier is far enough for a personal or professional account. Gmailsync tries to limit the requests according to Google recommendations to no reach the quota.

To create a new Google Cloud Platform project go to this link and create a new project:
[https://console.cloud.google.com/](https://console.cloud.google.com/)

Then you need to enable Gmail API for that project and generate a new OAuth 2.0 key and download it. This file will be the credentials file of the application in the context of gmailsync.

By default gmailsync reads the credentials from a file placed in the default gmailsync configuration directory, but you can customize this path in the configuration file.

## XDG User Directory support

Gmailsync supports XDG User Directories. That means you can place the global configuration files in `$XDG_CONFIG_HOME/gmailsync/` without the need to create any particular environment variable for this application or anything else.

If `$XDG_CONFIG_HOME` is not set, gmailsync automatically tries to use `~/.config/gmailsync`. If that directory does not exist, it tries to use `~/.gmailsync `.

## Configuration

Configuration options for gmailsync.

By default gmailsync uses the configuration file located in any of these paths (in this particular order):
 - `$XDG_CONFIG_HOME/gmailsync/config`
 - `~/.config/gmailsync/config`
 - `~/.gmailsync/config`

To specify a different path, you can use the `-c` option:

```bash
gmailsync -c another/config/file ...
```

The configuration file looks like this:

```python
[channel-starred]
mailbox: ~/mail/starred
query: label:starred

[channel-notifications]
mailbox: ~/mail/notifications
query: label:notifications
box_type: mbox

[channel-coworkers]
mailbox: ~/mail/coworkers
query: from:alice@gmail.com OR from:bob@gmail.com

[group-important]
channels: starred, coworkers
```

So, you could execute:
 - `gmailsync` to retrieve the new messages of all channels.
 - `gmailsync important` to retrieve the new messages of the channels "starred" and "coworkers".
 - `gmailsync notifications` to retrieve the new messages of the channel "notifications".
 - `gmailsync important notifications` to retrieve the new messages of the channels in the group "important" and in the channel "notifications".
 - Etc.

Configuration options are grouped in sections: general, channels, groups and log.

### General

General options of the application.

The section name in the configuration file is `general`.

Options:

| Option | Description | Mandatory | Default |
| --- | --- | --- | --- |
| `credentials`  | Path to the credentials file of your Google Cloud Platform project.  | No | `$XDG_CONFIG_HOME/gmailsync/credentials.json` or `~/.config/gmailsync/credentials.json` or `~/.gmailsync/credentials.json` |
| `token` | Path where the token file will be stored. This file contains the token for your associated Gmail account. | No | `$XDG_CONFIG_HOME/gmailsync/token.pickle` or `~/.config/gmailsync/token.pickle` or `~/.gmailsync/token.pickle` |
| `box_type` | Default box type for all channels. | No | `mailbox` |

Gmailsync supports the following mailbox types:
 - `maildir`
 - `mbox`
 - `mh`
 - `babyl`
 - `mmdf`

### Channels

Configuration of the channel.

The section names (one per channel) must follow this pattern: `channel-{channnel_name}`, where `{channel_name}` must be the name of the channel.

Options:

| Option | Description | Mandatory | Default |
| --- | --- | --- | --- |
| `mailbox` | Path to the directory where to store the messages. | Yes | |
| `query` | Optional query used to retrieve the messages. Supports the same query format as the Gmail search box. | No | `!in:chat` |
| `box_type` | Optional mailbox type. If it is not defined, the default one defined in `general` will be used. | No | |

### Groups

Configuration of the group.

The section names (one per group) must follow this pattern: `group-{group_name}`, where `{group}` must be the name of the group.

Options

| Option | Description | Mandatory | Default |
| --- | --- | --- | --- |
| `channels` | List of channel names separated by comma. | Yes | |

### Log

Configuration of the logger.

The section name in the configuration file is `log`.

Options:

| Option | Description | Mandatory | Default |
| --- | --- | --- | --- |
| `file` | Path to the file where the logs messages will be stored. | No | |
| `file_max_bytes` | Max bytes to store in the file before rotate it. | No | 104857600 (100 MB) |
| `file_backup_count` | Max files to keep before to remove the oldest one. | No | 50 |
| `format` | Log format for console and file logger. | No | `%(asctime)s %(levelname)s [%(name)s] %(message)s` |

### Full example

```python
[general]
credentials: /etc/gmailsync/credentials.json
token: /etc/gmailsync/token.pickle
box_type: mbox

[channel-starred]
mailbox: ~/mail/starred
query: label:starred

[channel-notifications]
mailbox: ~/mail/notifications
query: label:notifications
box_type: maildir

[channel-coworkers]
mailbox: ~/mail/coworkers
query: from:alice@gmail.com OR from:bob@gmail.com

[group-important]
channels: starred, coworkers

[log]
file: /var/log/gmailsync.log
```
