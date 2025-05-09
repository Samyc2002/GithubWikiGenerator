import os
import argparse
from scan_repo import scan_repo
from generate_wiki import generate_wiki, delete_dir


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
    args = parser.parse_args()
    delete_dir(args.output)

    print(f"Scanning repository: {args.repo}")
    context = scan_repo(args.repo)

    output_path = str(os.path.join(args.repo, args.output))
    print(f"Generating Wiki pages in: {output_path}")
    generate_wiki(context, output_path)


if __name__ == "__main__":
    main()
