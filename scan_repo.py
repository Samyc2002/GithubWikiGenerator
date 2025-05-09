import pathlib
import re
from get_code_summary import CodeAnalyzer


# List of file extensions to exclude
excluded_files = ["pem", "pack", "crt", "idx"]


def is_allowed_file(filename: str) -> bool:
    """
    Check if the file is allowed based on its name.
    :type filename: Name of the file to check
    :return: True if the file is allowed, False otherwise.
    """
    if filename.startswith("."):
        return False

    pattern = r"^(?!.*\.(" + "|".join(excluded_files) + ")$).*$"
    return bool(re.match(pattern, filename))


def is_allowed_folder(folder_name: str) -> bool:
    """
    Check if the folder is allowed based on its name.
    :type folder_name: Name of the folder to check
    :return: True if the folder is allowed, False otherwise.
    """
    return not (
            folder_name.startswith(".")
            or folder_name == "node_modules"
            or folder_name == "venv"
            or folder_name == "__pycache__"
            or folder_name.endswith("undodir")
    )


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


def list_directory_contents(path=".") -> dict:
    """
    Get the contents of a directory and its subdirectories.
    :param path: The path to the directory to scan.
    :return: A dictionary with the file names as keys and their descriptions as values.
    """
    directory = pathlib.Path(path)

    files = {}
    for item in directory.iterdir():
        if item.is_file() and is_allowed_file(item.name):
            file_metadata = read_file(f"{path}/{item.name}")
            files[file_metadata["name"]] = file_metadata["metadata"]["description"]
        elif item.is_dir() and is_allowed_folder(item.name):
            files_in_dir = list_directory_contents(f"{path}/{item.name}")
            files[item.name] = files_in_dir

    return files


def scan_repo(repo_path: str) -> dict:
    """
    Scan the GitHub repository for all files and directories.
    :param repo_path: The path to the Git repository.
    :return: A list of files and directories and their contents in the repository.
    """
    # Check if the provided path is a valid directory
    if not pathlib.Path(repo_path).is_dir():
        raise ValueError(
            f"The provided path is not a valid directory: {repo_path}")

    # List all files and directories in the repo
    contents = list_directory_contents(repo_path)

    return contents
