from tqdm import tqdm
import pathlib
from get_code_summary import CodeAnalyzer
from utils import is_allowed_file, is_allowed_folder, count_processable_files


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


def list_directory_contents(path=".", progress_bar=None) -> dict:
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
            if progress_bar:
                progress_bar.update(1)
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

    total_files = count_processable_files(repo_path)
    print(f"Found {total_files} files to process")

    # Create progress bar
    with tqdm(total=total_files, desc="Scanning files") as progress_bar:
        # List all files and directories in the repo
        contents = list_directory_contents(repo_path, progress_bar)

    return contents
