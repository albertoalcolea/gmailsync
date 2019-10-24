# gmailsync
Synchronize and save a backup of your Gmail messages

## Requirements

- python (3.3+)
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

### Usage

List Gmail labels:

```bash
gmailsync -l
```

Synchronize all channels

```bash
gmailsync
```

Synchronize concrete channels/groups

```bash
gmailsync group1 group2 channelXYZ
```