class ConfigurationError(ValueError):
    pass


class ConfigValidator:

    def validate(self, config):
        if not config.channels:
            raise ConfigurationError('No channels found in config')

        for group in config.groups.values():
            self._validate_group(config, group)

    def _validate_group(self, config, group):
        for channel in group.channels:
            if channel not in config.channels:
                raise ConfigurationError('Channel {!r} in group {!r} is not defined'.format(channel, group.name))