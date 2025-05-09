import os
import pathlib
import re


def count_processable_files(path=".") -> int:
    """
    Count the number of files that will be processed in a directory and its subdirectories.
    :param path: The path to the directory to scan.
    :return: The number of files that will be processed.
    """
    directory = pathlib.Path(path)

    count = 0
    for item in directory.iterdir():
        if item.is_file() and is_allowed_file(item.name):
            count += 1
        elif item.is_dir() and is_allowed_folder(item.name):
            count += count_processable_files(f"{path}/{item.name}")

    return count


def delete_dir(path: str) -> None:
    if not os.path.exists(path):
        return

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            delete_dir(item_path)
        elif os.path.isfile(item_path):
            os.remove(item_path)
    os.removedirs(path)


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
