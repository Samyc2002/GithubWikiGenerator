import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import subprocess
from get_code_summary import _check_gh_copilot, _sanitize_code, CodeAnalyzer

class TestGetCodeSummary(unittest.TestCase):
    @patch('subprocess.run')
    def test_check_gh_copilot_success(self, mock_run):
        # Test successful check
        _check_gh_copilot()
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_check_gh_copilot_failure(self, mock_run):
        # Test failure case
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh")
        with self.assertRaises(RuntimeError):
            _check_gh_copilot()

    def test_sanitize_code(self):
        # Test code sanitization
        code = "def example():\r\n    print('hello')\x00"
        sanitized = _sanitize_code(code)
        self.assertEqual(sanitized, "def example():\n    print('hello')")

    @patch('requests.post')
    def test_analyze_code_block(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "# Overview\nTest description\n# Key Features\n- Feature 1\n# Dependencies\n- None"}]}}
            ]
        }
        mock_post.return_value = mock_response

        analyzer = CodeAnalyzer()
        result = analyzer.analyze_code_block("def test(): pass", "test.py")

        self.assertIn("Overview", result)
        self.assertIn("Key Features", result)
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_analyze_code_block_timeout(self, mock_post):
        # Test timeout scenario
        mock_post.side_effect = subprocess.TimeoutExpired("command", 45)

        analyzer = CodeAnalyzer()
        result = analyzer.analyze_code_block("def test(): pass", "test.py")

        self.assertEqual(result, "Analysis timed out")

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    @patch('builtins.open', new_callable=mock_open, read_data="def test(): pass")
    @patch('get_code_summary.CodeAnalyzer.analyze_code_block')
    def test_analyze_file(self, mock_analyze_block, mock_file, mock_stat, mock_exists):
        # Setup mocks
        mock_exists.return_value = True
        mock_stat_result = MagicMock()
        mock_stat_result.st_size = 100
        mock_stat.return_value = mock_stat_result
        mock_analyze_block.return_value = "Test file description"

        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file("test.py")

        self.assertEqual(result["name"], "test.py")
        self.assertEqual(result["description"], "Test file description")

        # Test empty file
        mock_stat_result.st_size = 0
        result = analyzer.analyze_file("empty.py")
        self.assertEqual(result["description"], "Empty file")

        # Test non-existent file
        mock_exists.return_value = False
        result = analyzer.analyze_file("missing.py")
        self.assertIn("Error during analysis", result["description"])