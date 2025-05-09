import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from io import StringIO
import main

class TestMain(unittest.TestCase):
    @patch('sys.argv', ['main.py', '--repo', 'test_repo'])
    @patch('main.delete_dir')
    @patch('main.scan_repo')
    @patch('main.generate_wiki')
    @patch('os.path.join')
    def test_main_with_default_output(self, mock_join, mock_generate_wiki, mock_scan_repo, mock_delete_dir):
        # Setup mocks
        mock_scan_repo.return_value = {"test.py": "Test description"}
        mock_join.return_value = "test_repo/wiki"

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        main.main()

        # Reset stdout
        sys.stdout = sys.__stdout__

        # Assertions
        mock_delete_dir.assert_called_once_with("wiki")
        mock_scan_repo.assert_called_once_with("test_repo")
        mock_generate_wiki.assert_called_once_with({"test.py": "Test description"}, "test_repo/wiki")
        self.assertIn("Scanning repository: test_repo", captured_output.getvalue())

    @patch('sys.argv', ['main.py', '--repo', 'test_repo', '--output', 'custom_wiki'])
    @patch('main.delete_dir')
    @patch('main.scan_repo')
    @patch('main.generate_wiki')
    @patch('os.path.join')
    def test_main_with_custom_output(self, mock_join, mock_generate_wiki, mock_scan_repo, mock_delete_dir):
        # Setup mocks
        mock_scan_repo.return_value = {"test.py": "Test description"}
        mock_join.return_value = "test_repo/custom_wiki"

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        main.main()

        # Reset stdout
        sys.stdout = sys.__stdout__

        # Assertions
        mock_delete_dir.assert_called_once_with("custom_wiki")
        mock_scan_repo.assert_called_once_with("test_repo")
        mock_generate_wiki.assert_called_once_with({"test.py": "Test description"}, "test_repo/custom_wiki")
        self.assertIn("Generating Wiki pages in: test_repo/custom_wiki", captured_output.getvalue())