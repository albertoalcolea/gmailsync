# gmailsync
Synchronize and save a backup of your Gmail messages

## Requirements

- python (3.4+)
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

The free layer is far enough for some personal or professional accounts. Gmailsync tries to limit the requests according to Google recommendations to no reach the quota.

To create a new Google Cloud Platform project go to this link and create a new project:
[https://console.cloud.google.com/](https://console.cloud.google.com/)

Then you need to create a new OAuth 2.0 and download it. By default gmailsync takes this file from `~/.gmailsync-credentials.json`. You can customize this path in the configuration file.

This file will be the credentials file of the application in the context of gmailsync.


## Configuration

By default gmailsync uses this configuration file: `~/.gmailsync.conf`.

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

Configuration options are grouped in sections:
 - General: General options of the application.
 - Channels: Configuration of the channels. One section per channel.
 - Groups: Configuration of the groups. One section per group.
 - Log: Configuration of the logger.

### General

General options of the application. 

The section name in the configuration file is `general`.

Options:
| Option | Description | Mandatory | Default |
| --- | --- | --- | --- |
| `credentials`  | Path to the credentials file of your Google Cloud Platform project.  | No | `~/.gmailsync-credentials.json` |
| `token` | Path where the token file will be stored. This file contains the token for your associated Gmail account. | No | `~/.gmailsync-token.pickle` |
| `box_type` | Default box type for all channels. | No | `mailbox` |

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