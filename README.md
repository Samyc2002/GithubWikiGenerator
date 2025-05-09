# Github Wiki Generator

A small tool to generate Github Wiki Pages for documenting code file by file.

## Features
- Generates a wiki page for each file in the repository.
- Supports Code for all languages.
- Organizes files into folders with the same name as in the code.

## Usage
1. Clone the repository.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
    python main.py
    ```

## Available parameters
- `--repo`: Path to the directory containing the code files. Must be provided.
- `--output`: Path to the output directory for the wiki pages. Default is `wiki`.