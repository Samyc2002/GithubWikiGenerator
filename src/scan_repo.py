import os
import pathlib
import tempfile
from urllib.parse import urlparse
from git import Repo
from progress.bar import ChargingBar
from .get_code_summary import CodeAnalyzer
from .utils import is_allowed_file, is_allowed_folder, delete_dir, is_github_url, count_processable_files

GITHUB_AUTH_TOKEN = os.environ["GITHUB_AUTH_TOKEN"]


def read_file(file_path: str) -> dict:
    """
    Read file contents and return a metadata object with the file data.
    :param file_path: The path to the file.
    :return: A metadata object with the file data.
    """

    analyzer = CodeAnalyzer()

    # Check if the provided path is a valid file
    if not pathlib.Path(file_path).is_file():
        raise ValueError(f"The provided path is not a valid file: {file_path}")

    metadata = {
        "name": pathlib.Path(file_path).name,
        "metadata": analyzer.analyze_file(file_path),
    }

    return metadata


def clone_github_repo(github_url: str, auth_token: str = None) -> str:
    """
    Clone a GitHub repository to a temporary directory
    :param github_url: The GitHub repository URL
    :param auth_token: GitHub personal access token for private repos
    :return: Path to the cloned repository
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Parse the GitHub URL to get the repo name for better folder naming
    parsed_url = urlparse(github_url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) >= 2:
        repo_name = path_parts[1]
        clone_dir = os.path.join(temp_dir, repo_name)
    else:
        clone_dir = temp_dir

    # Modify URL to include auth token if provided
    if auth_token:
        auth_url = f"https://{GITHUB_AUTH_TOKEN}@github.com/{path_parts[0]}/{path_parts[1]}.git"
    else:
        auth_url = github_url

    # Clone the repository
    Repo.clone_from(auth_url, clone_dir)

    return clone_dir


def list_directory_contents(path=".", progress_bar: ChargingBar = None, ignore_file_path: str | None = None) -> dict:
    """
    Get the contents of a directory and its subdirectories.
    :param ignore_file_path: Path to the ignore file.
    :param path: The path to the directory to scan.
    :param progress_bar: A progress bar to show the scanning progress.
    :return: A dictionary with the file names as keys and their descriptions as values.
    """
    directory = pathlib.Path(path)

    files = {}
    for item in directory.iterdir():
        if item.is_file() and is_allowed_file(item.name, ignore_file_path):
            file_metadata = read_file(f"{path}/{item.name}")
            files[file_metadata["name"]] = file_metadata["metadata"]["description"]
            if progress_bar:
                progress_bar.next()
        elif item.is_dir() and is_allowed_folder(item.name, ignore_file_path):
            files_in_dir = list_directory_contents(f"{path}/{item.name}", progress_bar, ignore_file_path)
            files[item.name] = files_in_dir

    return files


def scan_git_repo(repo_path: str, ignore_file_path: str | None = None) -> dict:
    """
    Scan the Git repository for all files and directories.
    :param ignore_file_path: Path to the ignore file.
    :param repo_path: The path to the Git repository.
    :return: A list of files and directories and their contents in the repository.
    """
    local_path = repo_path

    # Check if the input is a GitHub URL
    if is_github_url(repo_path):
        # Clone the GitHub repository
        local_path = clone_github_repo(repo_path, GITHUB_AUTH_TOKEN)

    # Check if the provided path is a valid directory
    if not pathlib.Path(local_path).is_dir():
        raise ValueError(f"The provided path is not a valid directory: {local_path}")

    total_files, total_folders = count_processable_files(local_path, ignore_file_path)
    print(f"Found {total_files} file{"s" if total_files > 1 else ""} in {total_folders} folder{"s" if total_folders > 1 else ""} to analyze.")

    # Create a progress bar
    progress_bar = ChargingBar(f"Scanning repository: {pathlib.Path(local_path).name or local_path}", max=total_files,
                               suffix='%(index)d/%(max)d files (%(percent).1f%%)')

    # List all files and directories in the repo
    contents = list_directory_contents(local_path, progress_bar, ignore_file_path)

    # Clean up temporary directory
    parent_dir = os.path.dirname(local_path)
    delete_dir(parent_dir)

    return contents


def scan_repo(repo_path: str, progress_bar: ChargingBar = None, ignore_file_path: str | None = None) -> dict:
    """
    Scan the GitHub repository for all files and directories.
    :param repo_path: The path to the Git repository.
    :param progress_bar: A progress bar to show the scanning progress.
    :return: A list of files and directories and their contents in the repository.
    """
    # Check if the provided path is a valid directory
    if not pathlib.Path(repo_path).is_dir():
        if not pathlib.Path(repo_path).is_file():
            raise ValueError(f"The provided path is not a valid directory: {repo_path}")

        return { f"{repo_path}": read_file(repo_path)["metadata"]["description"] }

    # List all files and directories in the repo
    contents = list_directory_contents(repo_path, progress_bar, ignore_file_path)

    return contents
