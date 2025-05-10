import os
import pathlib
import re
import shutil
from urllib.parse import urlparse


def is_github_url(url: str) -> bool:
    """
    Check if the given string is a GitHub URL.
    :param url: The URL to check.
    :return: True if the URL is a GitHub URL, False otherwise.
    """
    if not isinstance(url, str):
        return False

    if not url.startswith(("http://", "https://")):
        return False

    parsed_url = urlparse(url)
    return parsed_url.netloc in ["github.com", "www.github.com"]


def count_processable_files(path=".", ignore_file_path: str | None = None) -> tuple[int, int]:
    """
    Count the number of files that will be processed in a directory and its subdirectories.
    :param ignore_file_path: Path to the ignore file.
    :param path: The path to the directory to scan.
    :return: The number of files that will be processed.
    """
    if pathlib.Path(path).is_file():
        return 1

    directory = pathlib.Path(path)

    file_count, folder_count = 0, 0
    for item in directory.iterdir():
        if item.is_file() and is_allowed_file(item.name, ignore_file_path):
            file_count += 1
        elif item.is_dir() and is_allowed_folder(item.name, ignore_file_path):
            files, folders = count_processable_files(f"{path}/{item.name}", ignore_file_path)
            file_count += files
            folder_count += (1 + folders)

    return file_count, folder_count


def delete_dir(path: str) -> None:
    dir_path = pathlib.Path(path)
    if dir_path.exists():
        shutil.rmtree(dir_path, ignore_errors=True)


# List of file extensions to exclude
excluded_files = {
    "ignore_hidden": True,
    "extensions": ["pem", "pack", "crt", "idx", "mp4", "avi", "mkv", "mov", "mp3", "wav", "flac", "aac", "gif", "png", "jpg", "jpeg", "bmp", "tiff", "webp", "svg", "ico", "zip", "tar", "gz", "bz2", "xz", "7z", "rar"],
}

# Excluded folders
excluded_folders = {
    "ignore_hidden": True,
    "extensions": ["node_modules", "venv", "__pycache__", "target"],
}


def glob_to_regex(pattern: str) -> str:
    """
    Convert a glob pattern to a regular expression pattern.
    :param pattern: The glob pattern to convert.
    :return: The equivalent regular expression pattern.
    """
    # Remove trailing slash for directory patterns
    if pattern.endswith('/'):
        pattern = pattern[:-1]

    # Escape all special regex characters
    pattern = re.escape(pattern)

    # Convert glob wildcards to regex wildcards
    # * (matches any sequence of characters) -> .*
    pattern = pattern.replace('\\*', '.*')
    # ? (matches any single character) -> .
    pattern = pattern.replace('\\?', '.')

    # Add start and end anchors
    pattern = f"^{pattern}$"

    return pattern


def get_user_excluded(ignore_file_path: str | None = None) -> list[str]:
    """
    Get the list of excluded files and folders from the user.
    :param ignore_file_path: Path to the ignore file.
    :return: List of excluded files and folders.
    """
    if not os.path.exists(ignore_file_path):
        return []

    with open(ignore_file_path, "r") as file:
        lines = file.readlines()

    excluded = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            excluded.append(glob_to_regex(line))

    return excluded


def is_allowed_file(filename: str, ignore_file_path: str | None = None) -> bool:
    """
    Check if the file is allowed based on its name.
    :param ignore_file_path: Path to the ignore file.
    :type filename: Name of the file to check
    :return: True if the file is allowed, False otherwise.
    """
    if excluded_files["ignore_hidden"] and filename.startswith("."):
        return False

    # Get excluded files from user
    if ignore_file_path:
        user_excluded_files = get_user_excluded(ignore_file_path)
        if user_excluded_files:
            for excluded in user_excluded_files:
                if re.match(excluded, filename):
                    return False

    # Check if the file extension is in the excluded list
    if any(filename.endswith(ext) for ext in excluded_files["extensions"]):
        return False

    return True

def is_allowed_folder(folder_name: str, ignore_file_path: str | None = None) -> bool:
    """
    Check if the folder is allowed based on its name.
    :param ignore_file_path: Path to the ignore file.
    :type folder_name: Name of the folder to check
    :return: True if the folder is allowed, False otherwise.
    """
    if excluded_folders["ignore_hidden"] and folder_name.startswith("."):
        return False

    # Get excluded files from user
    if ignore_file_path:
        user_excluded_files = get_user_excluded(ignore_file_path)
        if user_excluded_files:
            for excluded in user_excluded_files:
                if re.match(excluded, folder_name):
                    return False

    if folder_name in excluded_folders["extensions"]:
        return False

    return True