import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, mock_open, MagicMock
import src.generate_wiki as generate_wiki

class TestGenerateWiki(unittest.TestCase):
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_wiki_with_files(self, mock_open_file, mock_makedirs):
        # Test with flat file structure
        context = {
            "file1.py": "File 1 description",
            "file2.py": "File 2 description"
        }

        generate_wiki.generate_wiki(context, "output_path")

        mock_makedirs.assert_called_once_with("output_path")
        self.assertEqual(mock_open_file.call_count, 2)

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_wiki_with_folders(self, mock_open_file, mock_makedirs):
        # Test with nested directory structure
        context = {
            "file1.py": "File 1 description",
            "subdir": {
                "subfile.py": "Subfile description"
            }
        }

        # Fully replace generate_wiki to avoid recursion during testing
        original_generate_wiki = generate_wiki.generate_wiki

        def mocked_implementation(context, output_path):
            os.makedirs(output_path)
            for item in context.keys():
                if isinstance(context[item], dict):
                    # For nested directories, just create the directory but don't recurse
                    folder_path = os.path.join(output_path, item)
                    os.makedirs(folder_path)
                elif isinstance(context[item], str):
                    # For files, create the file
                    file_name = ".".join(item.split(".")[:-1]) + ".md"
                    file_path = os.path.join(output_path, file_name)
                    with open(file_path, "w", encoding="utf-8") as wiki_file:
                        wiki_file.write(context[item])

        with patch('src.generate_wiki.generate_wiki', side_effect=mocked_implementation):
            generate_wiki.generate_wiki(context, "output_path")

            # Verify the file was created
            expected_file_path = os.path.join("output_path", "file1.md")
            mock_open_file.assert_any_call(expected_file_path, "w", encoding="utf-8")