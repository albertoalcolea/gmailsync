import unittest
from unittest.mock import patch

from gmailsync.cli import color_text, cprint, Color, Status


class ColorTextTestCase(unittest.TestCase):

    def test_default_color(self):
        colored = color_text('This is a test')
        self.assertEqual(colored, 'This is a test')

    def test_bold_with_no_color(self):
        colored = color_text('This is a test', bold=True)
        self.assertEqual(colored, '\033[1mThis is a test\033[0m')

    def test_color(self):
        colored = color_text('This is a test', color=Color.GREEN)
        self.assertEqual(colored, '\033[32mThis is a test\033[0m')

    def test_color_bold(self):
        colored = color_text('This is a test', color=Color.BRIGHT_CYAN, bold=True)
        self.assertEqual(colored, '\033[96m\033[1mThis is a test\033[0m')

    def test_invalid_color(self):
        with self.assertRaisesRegex(ValueError, "'color' must be an item of 'Color' enum"):
            color_text('This is a test', color='invalid color')


class CPrintTestCase(unittest.TestCase):

    def setUp(self):
        self.print_patcher = patch('gmailsync.cli.print')
        self.mock_print = self.print_patcher.start()

    def tearDown(self):
        self.print_patcher.stop()

    def test_default_color(self):
        cprint('This is a test')
        self.mock_print.assert_called_with('This is a test')

    def test_bold_with_no_color(self):
        cprint('This is a test', bold=True)
        self.mock_print.assert_called_with('\033[1mThis is a test\033[0m')

    def test_color(self):
        cprint('This is a test', color=Color.RED)
        self.mock_print.assert_called_with('\033[31mThis is a test\033[0m')

    def test_status(self):
        cprint('This is a test', status=Status.WARNING)
        self.mock_print.assert_called_with('\033[33m\033[1mThis is a test\033[0m')

    def test_status_has_preference_over_color_and_bold(self):
        cprint('This is a test', color=Color.RED, status=Status.SUCCESS, bold=False)
        self.mock_print.assert_called_with('\033[32m\033[1mThis is a test\033[0m')

    def test_invalid_color(self):
        with self.assertRaisesRegex(ValueError, "'color' must be an item of 'Color' enum"):
            cprint('This is a test', color='invalid color')
        self.mock_print.assert_not_called()

    def test_invalid_status(self):
        with self.assertRaisesRegex(ValueError, "'status' must be an item of 'Status' enum"):
            cprint('This is a test', status='invalid status')
        self.mock_print.assert_not_called()