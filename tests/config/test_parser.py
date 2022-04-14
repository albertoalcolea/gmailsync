import unittest
from unittest.mock import patch, call
import os

from gmailsync.config.parser import EnhancedConfigParser


class EnhancedConfigParserReadTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = EnhancedConfigParser()

    @patch('gmailsync.config.parser.RawConfigParser.read')
    @patch('gmailsync.config.parser.expand_path')
    def test_expand_single_filename_in_read(self, mock_expand_path, mock_super_read):
        mock_expand_path.side_effect = lambda path: path
        parser = EnhancedConfigParser()
        parser.read('~/.config/.gmailsync.conf', encoding='utf-8')
        mock_expand_path.assert_called_once_with('~/.config/.gmailsync.conf')
        mock_super_read.assert_called_once_with(['~/.config/.gmailsync.conf'], 'utf-8')

    @patch('gmailsync.config.parser.RawConfigParser.read')
    @patch('gmailsync.config.parser.expand_path')
    def test_expand_multiple_filenames_in_read(self, mock_expand_path, mock_super_read):
        mock_expand_path.side_effect = lambda path: path
        parser = EnhancedConfigParser()
        parser.read(['/a.conf', '/b.conf'])
        mock_expand_path.assert_has_calls([call('/a.conf'), call('/b.conf')])
        mock_super_read.assert_called_once_with(['/a.conf', '/b.conf'], None)


class EnhancedConfigParserPathTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = EnhancedConfigParser()
        self.parser.read_dict({
            'section1': {
                'path': '/foo'
            }
        })

        self.isfile_patcher = patch('gmailsync.config.parser.os.path.isfile')
        self.mock_isfile = self.isfile_patcher.start()

        self.isdir_patcher = patch('gmailsync.config.parser.os.path.isdir')
        self.mock_isdir = self.isdir_patcher.start()

        self.access_patcher = patch('gmailsync.config.parser.os.access')
        self.mock_access = self.access_patcher.start()

    def tearDown(self):
        self.isfile_patcher.stop()
        self.isdir_patcher.stop()
        self.access_patcher.stop()

    @patch('gmailsync.config.parser.expand_path')
    def test_expand_path(self, mock_expand_path):
        mock_expand_path.side_effect = lambda path: path
        path = self.parser.getpath('section1', 'path')
        self.assertEqual(path, '/foo')
        mock_expand_path.assert_called_once_with('/foo')

    def test_as_file(self):
        self.mock_isfile.return_value = True
        path = self.parser.getpath('section1', 'path', is_file=True)
        self.assertEqual(path, '/foo')

    def test_as_file_if_not_file(self):
        self.mock_isfile.return_value = False
        with self.assertRaisesRegex(ValueError, "Path must be an existing file: '/foo'"):
            self.parser.getpath('section1', 'path', is_file=True)

    def test_as_dir(self):
        self.mock_isdir.return_value = True
        path = self.parser.getpath('section1', 'path', is_dir=True)
        self.assertEqual(path, '/foo')

    def test_as_dir_if_not_dir(self):
        self.mock_isdir.return_value = False
        with self.assertRaisesRegex(ValueError, "Path must be an existing directory: '/foo'"):
            self.parser.getpath('section1', 'path', is_dir=True)

    def test_as_readable_without_is_file_nor_dir(self):
        exc_msg = "'readable' and 'writable' options are available only with 'is_file' or 'is_dir'"
        with self.assertRaisesRegex(ValueError, exc_msg):
            self.parser.getpath('section1', 'path', readable=True)

    def test_as_writable_without_is_file_nor_dir(self):
        exc_msg = "'readable' and 'writable' options are available only with 'is_file' or 'is_dir'"
        with self.assertRaisesRegex(ValueError, exc_msg):
            self.parser.getpath('section1', 'path', readable=True)

    def test_as_readable_file(self):
        self.mock_isfile.return_value = True
        self.mock_access.return_value = True
        path = self.parser.getpath('section1', 'path', is_file=True, readable=True)
        self.assertEqual(path, '/foo')
        self.mock_access.assert_called_once_with('/foo', os.F_OK | os.R_OK)

    def test_as_readable_file_if_not_readable(self):
        self.mock_isfile.return_value = True
        self.mock_access.return_value = False
        with self.assertRaisesRegex(ValueError, "Path must be readable. Check permissions: '/foo'"):
            self.parser.getpath('section1', 'path', is_file=True, readable=True)
        self.mock_access.assert_called_once_with('/foo', os.F_OK | os.R_OK)

    def test_as_writable_file(self):
        self.mock_isfile.return_value = True
        self.mock_access.return_value = True
        path = self.parser.getpath('section1', 'path', is_file=True, writable=True)
        self.assertEqual(path, '/foo')
        self.mock_access.assert_called_once_with('/foo', os.F_OK | os.W_OK)

    def test_as_writable_file_if_not_writable(self):
        self.mock_isfile.return_value = True
        self.mock_access.return_value = False
        with self.assertRaisesRegex(ValueError, "Path must be writable. Check permissions: '/foo'"):
            self.parser.getpath('section1', 'path', is_file=True, writable=True)
        self.mock_access.assert_called_once_with('/foo', os.F_OK | os.W_OK)

    def test_as_readable_dir(self):
        self.mock_isdir.return_value = True
        self.mock_access.return_value = True
        path = self.parser.getpath('section1', 'path', is_dir=True, readable=True)
        self.assertEqual(path, '/foo')
        self.mock_access.assert_called_once_with('/foo', os.F_OK | os.X_OK | os.R_OK)

    def test_as_readable_dir_if_not_readable(self):
        self.mock_isdir.return_value = True
        self.mock_access.return_value = False
        with self.assertRaisesRegex(ValueError, "Path must be readable. Check permissions: '/foo'"):
            self.parser.getpath('section1', 'path', is_dir=True, readable=True)
        self.mock_access.assert_called_once_with('/foo', os.F_OK | os.X_OK | os.R_OK)

    def test_as_writable_dir(self):
        self.mock_isdir.return_value = True
        self.mock_access.return_value = True
        path = self.parser.getpath('section1', 'path', is_dir=True, writable=True)
        self.assertEqual(path, '/foo')
        self.mock_access.assert_called_once_with('/foo', os.F_OK | os.X_OK | os.W_OK)

    def test_as_writable_dir_if_not_writable(self):
        self.mock_isdir.return_value = True
        self.mock_access.return_value = False
        with self.assertRaisesRegex(ValueError, "Path must be writable. Check permissions: '/foo'"):
            self.parser.getpath('section1', 'path', is_dir=True, writable=True)
        self.mock_access.assert_called_once_with('/foo', os.F_OK | os.X_OK | os.W_OK)

    @patch('gmailsync.config.parser.expand_path')
    def test_fallback_none(self, mock_expand_path):
        path = self.parser.getpath('nosection', 'nooption', fallback=None)
        self.assertIsNone(path)
        mock_expand_path.assert_not_called()


class EnhancedConfigParserListTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = EnhancedConfigParser()
        self.parser.read_dict({
            'section2': {
                'opt1': 'this is not a list',
                'opt2': 'aa, bb, cc',
                'opt3': ' aa   ,  bb ,  cc  ',
                'opt4': 'aa, bb|cc|dd',
            }
        })

    def test_no_list(self):
        elems = self.parser.getlist('section2', 'opt1')
        self.assertEqual(elems, ['this is not a list'])

    def test_list(self):
        elems = self.parser.getlist('section2', 'opt2')
        self.assertEqual(elems, ['aa', 'bb', 'cc'])

    def test_strip_elements(self):
        elems = self.parser.getlist('section2', 'opt3')
        self.assertEqual(elems, ['aa', 'bb', 'cc'])

    def test_custom_separator(self):
        elems = self.parser.getlist('section2', 'opt4', sep='|')
        self.assertEqual(elems, ['aa, bb', 'cc', 'dd'])

    def test_fallback_none(self):
        elems = self.parser.getlist('nosection', 'nooption', fallback=None)
        self.assertIsNone(elems)
