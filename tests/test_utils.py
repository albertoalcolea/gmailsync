import unittest

from tests.utils import override_environ

from gmailsync.utils import chunked, expand_path


class ChunkedTestCase(unittest.TestCase):

    def test_chunked(self):
        iterable = [1, 2, 3, 4, 5, 6, 7]
        generator = chunked(iterable, 3)
        self.assertEqual(next(generator), (1, 2, 3))
        self.assertEqual(next(generator), (4, 5, 6))
        self.assertEqual(next(generator), (7,))
        with self.assertRaises(StopIteration):
            next(generator)


class ExpandPathTestCase(unittest.TestCase):

    def test_expand_path_absolute(self):
        path = expand_path('/home/user/dir')
        self.assertEqual(path, '/home/user/dir')

    def test_expand_path_relative(self):
        path = expand_path('/home/user/../dir')
        self.assertEqual(path, '/home/dir')

    def test_expand_path_home(self):
        with override_environ(HOME='/home/james'):
            path = expand_path('~/dir')
            self.assertEqual(path, '/home/james/dir')

    def test_expand_path_env(self):
        with override_environ(gmailsynctest='foo'):
            path = expand_path('/opt/$gmailsynctest/bar/${gmailsynctest}')
            self.assertEqual(path, '/opt/foo/bar/foo')
