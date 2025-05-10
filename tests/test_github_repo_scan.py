import unittest
from unittest import mock
import os
import tempfile
import pathlib
from src.utils import is_github_url
from src.scan_repo import clone_github_repo, scan_git_repo

class TestGitHubFunctions(unittest.TestCase):

    def test_is_github_url(self):
        """Test the is_github_url function with various inputs."""
        # Valid GitHub URLs
        self.assertTrue(is_github_url("https://github.com/username/repo"))
        self.assertTrue(is_github_url("http://github.com/username/repo"))
        self.assertTrue(is_github_url("https://www.github.com/username/repo"))

        # Invalid URLs
        self.assertFalse(is_github_url("https://gitlab.com/username/repo"))
        self.assertFalse(is_github_url("github.com/username/repo"))  # Missing protocol
        self.assertFalse(is_github_url("http://example.com/path"))
        self.assertFalse(is_github_url(None))
        self.assertFalse(is_github_url(123))

    @mock.patch('src.scan_repo.Repo')
    @mock.patch('src.scan_repo.tempfile.mkdtemp')
    def test_clone_github_repo(self, mock_mkdtemp, mock_repo):
        """Test the clone_github_repo function."""
        # Setup mocks
        mock_temp_dir = "/tmp/temp_dir"
        mock_mkdtemp.return_value = mock_temp_dir

        # Test without auth token
        url = "https://github.com/username/repo"
        expected_clone_dir = os.path.join(mock_temp_dir, "repo")

        result = clone_github_repo(url)

        mock_mkdtemp.assert_called_once()
        mock_repo.clone_from.assert_called_once()
        self.assertEqual(result, expected_clone_dir)

        # Reset mocks
        mock_mkdtemp.reset_mock()
        mock_repo.reset_mock()
        mock_mkdtemp.return_value = mock_temp_dir

        # Test with auth token
        auth_token = "test_token"
        with mock.patch('src.scan_repo.GITHUB_AUTH_TOKEN', auth_token):
            result = clone_github_repo(url, auth_token)

            mock_mkdtemp.assert_called_once()
            mock_repo.clone_from.assert_called_once()
            self.assertEqual(result, expected_clone_dir)

    @mock.patch('src.scan_repo.clone_github_repo')
    @mock.patch('src.scan_repo.list_directory_contents')
    @mock.patch('src.scan_repo.count_processable_files')
    @mock.patch('src.scan_repo.delete_dir')
    @mock.patch('src.scan_repo.is_github_url')
    @mock.patch('src.scan_repo.ChargingBar')
    @mock.patch('pathlib.Path')
    def test_scan_git_repo(self, mock_path, mock_bar, mock_is_github_url,
                         mock_delete_dir, mock_count_files, mock_list_contents, mock_clone):
        """Test the scan_git_repo function with both local and GitHub URL inputs."""
        # Setup common mocks
        mock_contents = {"file1.py": "description1"}
        mock_list_contents.return_value = mock_contents
        mock_count_files.return_value = 10

        # Setup Path mock
        mock_path_instance = mock.MagicMock()
        mock_path_instance.is_dir.return_value = True
        mock_path_instance.name = "test_repo"
        mock_path.return_value = mock_path_instance

        # Test with local path
        mock_is_github_url.return_value = False
        local_path = "/path/to/local/repo"

        result = scan_git_repo(local_path)

        mock_clone.assert_not_called()
        mock_path.assert_called_with(local_path)
        mock_list_contents.assert_called_with(local_path, mock.ANY)
        self.assertEqual(result, mock_contents)

        # Reset mocks
        mock_is_github_url.reset_mock()
        mock_clone.reset_mock()
        mock_path.reset_mock()
        mock_list_contents.reset_mock()

        # Test with GitHub URL
        mock_is_github_url.return_value = True
        cloned_path = "/tmp/cloned_repo"
        mock_clone.return_value = cloned_path
        github_url = "https://github.com/username/repo"

        result = scan_git_repo(github_url)

        mock_clone.assert_called_once_with(github_url, mock.ANY)
        mock_path.assert_called_with(cloned_path)
        mock_list_contents.assert_called_with(cloned_path, mock.ANY)
        mock_delete_dir.assert_called()
        self.assertEqual(result, mock_contents)

        # Test error case for invalid directory
        mock_path_instance.is_dir.return_value = False

        with self.assertRaises(ValueError):
            scan_git_repo("/invalid/path")


if __name__ == "__main__":
    unittest.main()