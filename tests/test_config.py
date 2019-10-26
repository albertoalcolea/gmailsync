import unittest
from unittest.mock import patch
import os
import logging
import logging.handlers

from gmailsync.config import LoggerConfig, to_path, to_int, set_up_logger


class ConfigToPathConversorTestCase(unittest.TestCase):

    def test_to_path(self):
        path = to_path('~/../file')
        self.assertEqual(path, '/home/file')

    @patch('gmailsync.config.os.path.isfile')
    def test_to_path_as_file(self, mock_isfile):
        mock_isfile.return_value = True

        path = to_path('~/../file', is_file=True)
        self.assertEqual(path, '/home/file')

        mock_isfile.assert_called_with('/home/file')

    @patch('gmailsync.config.os.path.isfile')
    def test_to_path_as_file_if_not_file(self, mock_isfile):
        mock_isfile.return_value = False

        exc_msg = 'Invalid value in config file. <~/../file> should be a valid file'
        with self.assertRaisesRegex(ValueError, exc_msg):
            to_path('~/../file', is_file=True)

        mock_isfile.assert_called_with('/home/file')

    @patch('gmailsync.config.os.path.isfile')
    @patch('gmailsync.config.os.access')
    def test_to_path_as_readable_file(self, mock_access, mock_isfile):
        mock_isfile.return_value = True
        mock_access.return_value = True

        path = to_path('~/../file', is_file=True, can_read=True)
        self.assertEqual(path, '/home/file')

        mock_isfile.assert_called_with('/home/file')
        mock_access.assert_called_with('/home/file', os.R_OK)

    @patch('gmailsync.config.os.path.isfile')
    @patch('gmailsync.config.os.access')
    def test_to_path_as_readable_file_if_not_file(self, mock_access, mock_isfile):
        mock_isfile.return_value = False

        exc_msg = 'Invalid value in config file. <~/../file> should be a valid file'
        with self.assertRaisesRegex(ValueError, exc_msg):
            to_path('~/../file', is_file=True, can_read=True)

        mock_isfile.assert_called_with('/home/file')
        mock_access.asert_not_called()

    @patch('gmailsync.config.os.path.isfile')
    @patch('gmailsync.config.os.access')
    def test_to_path_as_readable_file_if_not_readable(self, mock_access, mock_isfile):
        mock_isfile.return_value = True
        mock_access.return_value = False

        exc_msg = 'Invalid value in config file. <~/../file> should be a readable file. Check permissions'
        with self.assertRaisesRegex(ValueError, exc_msg):
            to_path('~/../file', is_file=True, can_read=True)

        mock_isfile.assert_called_with('/home/file')
        mock_access.assert_called_with('/home/file', os.R_OK)

    def test_to_path_with_none(self):
        exc_msg = 'Invalid value in config file. <None> should be a path'
        with self.assertRaisesRegex(ValueError, exc_msg):
            to_path(None)


class ConfigToIntConversorTestCase(unittest.TestCase):

    def test_to_int_with_int_number(self):
        integer = to_int('34')
        self.assertEqual(integer, 34)

    def test_to_int_with_float_number(self):
        exc_msg = 'Invalid value in config file. <34.49> should be an int'
        with self.assertRaisesRegex(ValueError, exc_msg):
            to_int('34.49')

    def test_to_int_with_not_number(self):
        exc_msg = 'Invalid value in config file. <abc> should be an int'
        with self.assertRaisesRegex(ValueError, exc_msg):
            to_int('abc')
            self.assertEqual(cm.exception, )

    def test_to_int_with_none(self):
        exc_msg = 'Invalid value in config file. <None> should be an int'
        with self.assertRaisesRegex(ValueError, exc_msg):
            to_int(None)


class ConfigSetUpLoggerTestCase(unittest.TestCase):

    DEFAULT_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    DEFAULT_MAX_BYTES = 104857600
    DEFAULT_BACKUP_COUNT = 500

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
        conf = LoggerConfig()
        set_up_logger(verbose=False, conf=conf)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)
        self._verify_console_handler(logger.handlers[0], self.DEFAULT_FORMAT)

    def test_verbose(self):
        conf = LoggerConfig()
        set_up_logger(verbose=True, conf=conf)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 1)
        self._verify_console_handler(logger.handlers[0], self.DEFAULT_FORMAT)

    @patch('builtins.open')
    def test_file_with_default_config(self, mock_open):
        conf = LoggerConfig()
        conf.file = '/home/user/.gmailsync.log'
        set_up_logger(verbose=True, conf=conf)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 2)
        self._verify_console_handler(logger.handlers[0], self.DEFAULT_FORMAT)
        self._verify_file_handler(logger.handlers[1], '/home/user/.gmailsync.log',
            self.DEFAULT_MAX_BYTES, self.DEFAULT_BACKUP_COUNT, self.DEFAULT_FORMAT)

    @patch('builtins.open')
    def test_file_with_customn_config(self, mock_open):
        conf = LoggerConfig()
        conf.file = '/home/user/.gmailsync.log'
        conf.file_max_bytes = 50
        conf.file_backup_count = 3
        set_up_logger(verbose=True, conf=conf)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 2)
        self._verify_console_handler(logger.handlers[0], self.DEFAULT_FORMAT)
        self._verify_file_handler(logger.handlers[1], '/home/user/.gmailsync.log', 50, 3,
            self.DEFAULT_FORMAT)

    @patch('builtins.open')
    def test_custom_format(self, mock_open):
        conf = LoggerConfig()
        conf.file = '/home/user/.gmailsync.log'
        conf.format = '%(message)s'
        set_up_logger(verbose=False, conf=conf)

        logger = logging.getLogger('gmailsync')

        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 2)
        self._verify_console_handler(logger.handlers[0], '%(message)s')
        self._verify_file_handler(logger.handlers[1], '/home/user/.gmailsync.log',
            self.DEFAULT_MAX_BYTES, self.DEFAULT_BACKUP_COUNT, '%(message)s')

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