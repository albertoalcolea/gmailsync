import unittest
from unittest.mock import patch
import logging
import logging.handlers


from gmailsync.config import set_up_logger
from gmailsync.config.models import LoggerConfig
from gmailsync.config.models import DEFAULT_LOG_MAX_BYTES, DEFAULT_LOG_BACKUP_COUNT, DEFAULT_LOG_FORMAT


class ConfigSetUpLoggerTestCase(unittest.TestCase):

    def setUp(self):
        # Backup previous logger
        self._logger_bkp = logging.Logger.manager.loggerDict.get('gmailsync')
        del logging.Logger.manager.loggerDict['gmailsync']

    def tearDown(self):
        # Restore previous logger
        if self._logger_bkp is not None:
            logging.Logger.manager.loggerDict['gmailsync'] = self._logger_bkp
        else:
            del logging.Logger.manager.loggerDict['gmailsync']

    def test_default(self):
        config = LoggerConfig()
        set_up_logger(verbose=False, config=config)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)
        self._verify_console_handler(logger.handlers[0], DEFAULT_LOG_FORMAT)

    def test_verbose(self):
        config = LoggerConfig()
        set_up_logger(verbose=True, config=config)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 1)
        self._verify_console_handler(logger.handlers[0], DEFAULT_LOG_FORMAT)

    @patch('builtins.open')
    def test_file_with_default_config(self, mock_open):
        config = LoggerConfig(file='/gmailsync.log')
        set_up_logger(verbose=True, config=config)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 2)
        self._verify_console_handler(logger.handlers[0], DEFAULT_LOG_FORMAT)
        self._verify_file_handler(logger.handlers[1], '/gmailsync.log', DEFAULT_LOG_MAX_BYTES,
                                  DEFAULT_LOG_BACKUP_COUNT, DEFAULT_LOG_FORMAT)

    @patch('builtins.open')
    def test_file_with_customn_config(self, mock_open):
        config = LoggerConfig(file='/gmailsync.log', max_bytes=50, backup_count=3)
        set_up_logger(verbose=True, config=config)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 2)
        self._verify_console_handler(logger.handlers[0], DEFAULT_LOG_FORMAT)
        self._verify_file_handler(logger.handlers[1], '/gmailsync.log', 50, 3, DEFAULT_LOG_FORMAT)

    @patch('builtins.open')
    def test_custom_format(self, mock_open):
        config = LoggerConfig(file='/gmailsync.log', format='%(message)s')
        set_up_logger(verbose=False, config=config)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 2)
        self._verify_console_handler(logger.handlers[0], '%(message)s')
        self._verify_file_handler(logger.handlers[1], '/gmailsync.log', DEFAULT_LOG_MAX_BYTES,
                                  DEFAULT_LOG_BACKUP_COUNT, '%(message)s')

    def _verify_console_handler(self, handler, log_format):
        self.assertTrue(isinstance(handler, logging.StreamHandler))
        self.assertEqual(handler.level, logging.DEBUG)
        self._verify_formatter(handler.formatter, log_format)

    def _verify_file_handler(self, handler, path, max_bytes, backup_count, log_format):
        self.assertTrue(isinstance(handler, logging.handlers.RotatingFileHandler))
        self.assertEqual(handler.baseFilename, path)
        self.assertEqual(handler.mode, 'a')
        self.assertEqual(handler.maxBytes, max_bytes)
        self.assertEqual(handler.backupCount, backup_count)
        self._verify_formatter(handler.formatter, log_format)

    def _verify_formatter(self, formatter, log_format):
        self.assertEqual(formatter._fmt, log_format)
