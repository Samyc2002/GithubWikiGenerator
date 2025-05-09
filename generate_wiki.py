import os


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


def generate_wiki(context: dict, output_path: str) -> None:
    """
    Generate Wiki pages for the repository.
    :param context: List of files and directories and their contents in the repository.
    :param output_path: The path to the output directory where the wiki pages will be saved (in .md format).
    :return: None
    """
    os.makedirs(output_path)
    for item in context.keys():
        if isinstance(context[item], dict):
            # This is a folder
            folder_path = os.path.join(output_path, item)
            generate_wiki(context[item], folder_path)
        elif isinstance(context[item], str):
            # This is a file
            file_name = ".".join(item.split(".")[:-1]) + ".md"
            file_path = os.path.join(output_path, file_name)
            if context[item]:
                with open(file_path, "w", encoding="utf-8") as wiki_file:
                    wiki_file.write(context[item])