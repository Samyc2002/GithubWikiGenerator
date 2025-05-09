import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import pathlib
from scan_repo import read_file, list_directory_contents, scan_repo
from utils import is_allowed_file, is_allowed_folder


class TestScanRepo(unittest.TestCase):
    def test_is_allowed_file(self):
        # Test allowed files
        self.assertTrue(is_allowed_file("main.py"))
        self.assertTrue(is_allowed_file("README.md"))
        self.assertTrue(is_allowed_file("data.json"))

        # Test excluded files
        self.assertFalse(is_allowed_file("cert.pem"))
        self.assertFalse(is_allowed_file("data.pack"))
        self.assertFalse(is_allowed_file("cert.crt"))
        self.assertFalse(is_allowed_file("repo.idx"))
        self.assertFalse(is_allowed_file(".gitignore"))

    def test_is_allowed_folder(self):
        # Test allowed folders
        self.assertTrue(is_allowed_folder("src"))
        self.assertTrue(is_allowed_folder("tests"))
        self.assertTrue(is_allowed_folder("docs"))

        # Test excluded folders
        self.assertFalse(is_allowed_folder(".git"))
        self.assertFalse(is_allowed_folder("node_modules"))
        self.assertFalse(is_allowed_folder("venv"))
        self.assertFalse(is_allowed_folder("__pycache__"))
        self.assertFalse(is_allowed_folder("vim_undodir"))

    @patch('pathlib.Path.is_file')
    @patch('scan_repo.CodeAnalyzer')
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

    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.is_dir')
    @patch('scan_repo.read_file')
    def test_list_directory_contents(self, mock_read_file, mock_is_dir, mock_is_file, mock_iterdir):
        # Setup mocks for a directory with a file and a subdirectory
        mock_file = MagicMock()
        mock_file.name = "test.py"
        mock_file.is_file.return_value = True
        mock_file.is_dir.return_value = False

        mock_dir = MagicMock()
        mock_dir.name = "subdir"
        mock_dir.is_file.return_value = False
        mock_dir.is_dir.return_value = True

        mock_iterdir.return_value = [mock_file, mock_dir]
        mock_read_file.return_value = {"name": "test.py", "metadata": {"description": "Test file"}}

        with patch('scan_repo.list_directory_contents', wraps=list_directory_contents) as wrapped_func:
            wrapped_func.side_effect = lambda path: {"subfile.py": "Subfile description"} if "subdir" in path else wrapped_func(path)

            result = list_directory_contents("test_path")

            self.assertIn("test.py", result)
            self.assertEqual(result["test.py"], "Test file")
            self.assertIn("subdir", result)
            self.assertEqual(result["subdir"]["subfile.py"], "Subfile description")

    @patch('pathlib.Path.is_dir')
    @patch('scan_repo.list_directory_contents')
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