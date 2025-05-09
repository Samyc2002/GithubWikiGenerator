import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from src.scan_repo import read_file, scan_repo


class TestScanRepo(unittest.TestCase):
    @patch('pathlib.Path.is_file')
    @patch('src.scan_repo.CodeAnalyzer')
    def test_read_file(self, mock_analyzer, mock_is_file):
        # Setup mocks
        mock_is_file.return_value = True
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.analyze_file.return_value = {"description": "Test description"}

        # Test valid file
        result = read_file("test_file.py")
        self.assertEqual(result["name"], "test_file.py")
        self.assertEqual(result["metadata"], {"description": "Test description"})

        # Test invalid file
        mock_is_file.return_value = False
        with self.assertRaises(ValueError):
            read_file("invalid_file.py")

    @patch('pathlib.Path.is_dir')
    @patch('src.scan_repo.list_directory_contents')
    def test_scan_repo(self, mock_list_contents, mock_is_dir):
        # Setup mocks
        mock_is_dir.return_value = True
        mock_list_contents.return_value = {"file.py": "Test description"}

        result = scan_repo("test_repo")
        self.assertEqual(result, {"file.py": "Test description"})

        # Test invalid directory
        mock_is_dir.return_value = False
        with self.assertRaises(ValueError):
            scan_repo("invalid_repo")