from dotenv import load_dotenv
import os
import argparse
import pathlib

from progress.bar import ChargingBar
from .scan_repo import scan_repo, scan_git_repo
from .generate_wiki import generate_wiki
from .utils import delete_dir, count_processable_files, is_github_url


load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="A Github Wiki Generator")
    parser.add_argument(
        "--repo",
        required=True,
        help="The path to the Git repository for which the wiki will be generated",
    )
    parser.add_argument(
        "--output",
        required=False,
        default="wiki",
        help="The path to the output directory where the wiki pages will be saved (in .md format)",
    )
    parser.add_argument(
        "--ignore_file",
        required=False,
        default=None,
        help="The path to the output directory where the wiki pages will be saved (in .md format)",
    )
    args = parser.parse_args()

    if is_github_url(args.repo):
        delete_dir(args.output)
        context = scan_git_repo(args.repo, args.ignore_file)

        print(f"\nGenerating Wiki pages in: {args.output}")
        generate_wiki(context, args.output)
        return

    output_path = str(os.path.join(args.repo, args.output))

    if os.path.isfile(args.repo):
        output_path = args.output

    delete_dir(output_path)

    total_files, total_folders = count_processable_files(args.repo, args.ignore_file)
    print(f"Found {total_files} file{"s" if total_files > 1 else ""} in {total_folders} folder{"s" if total_folders > 1 else ""} to analyze.")

    # Create progress bar
    progress_bar = ChargingBar(f"Scanning repository: {pathlib.Path(args.repo).name or args.repo}", max=total_files, suffix='%(index)d/%(max)d files (%(percent).1f%%)')
    context = scan_repo(args.repo, progress_bar, args.ignore_file)

    print(f"\nGenerating Wiki pages in: {output_path}")
    generate_wiki(context, output_path)


if __name__ == "__main__":
    main()
