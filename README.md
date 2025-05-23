# Github Wiki Generator

A small tool to generate GitHub Wiki Pages for documenting code file by file.

Ever had any of these thoughts?
- I wish I could have someone document my code.
- I wish there was an explanation for each file in this new codebase.
- Man I need to go through all these files to understand what they do.

No? Well, I did. So I made this tool to help me out. It generates a wiki page for each file in the repository, with a brief description of what the file does and how it works. The script uses the Gemini API to generate the wiki pages, so you need to have a Gemini API key to use it.

And as the name suggests, it generates wiki pages for GitHub repositories. The script is designed to be run from the command line, and it takes a single argument: the path to the directory containing the code files. The script will then generate a wiki page for each file in the directory and its subdirectories in the exact folder structure the code is in.

Here's a small demo of the script in action, generating wiki pages for itself:

![Demo](demo/demo.gif)

PS: This README is not generated by the script in case you were wondering :)

## Table of Contents
- [Features](#features)
- [Usage](#usage)
- [Available parameters](#available-parameters)
- [Prerequisites](#prerequisites)
- [FAQs](#faqs)
- [Want more features?](#want-more-features)

## Features
- Generates a wiki page for each file in the repository using Gemini API.
- Supports Code for all languages.
- Organizes files into folders with the same name as in the code.
- Exclude files and folders using regex patterns.

## Usage
1. Clone the repository.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Add environment variables for the Gemini API key and GitHub API key:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   export GITHUB_AUTH_TOKEN=your_api_key_here
   ```
4. Run the script:
   ```bash
    python3 -m src --repo path/to/your/repo --output optional/path/to/output
    ```
**NOTE**: Files and folders like `.git`, `__pycache__`, and `node_modules` are excluded by default. You can have more files and folders excluded by specifying a file path to ignore file path in "--ignore_file" parameter, like so:
```bash
python3 -m src --repo path/to/your/repo --output optional/path/to/output --ignore_file path/to/ignore_file
```

## Available parameters
- `--repo`: Path to the directory containing the code files. Must be provided.
- `--output`: Path to the output directory for the wiki pages. Default is `wiki`.
- `--ignore_file`: Path to a file containing regex patterns for files and folders to ignore.

## Prerequisites

- Python 3.x
- pip
- Git (for cloning the repository)
- Markdown (for generating wiki pages)
- A Gemini API key (for generating wiki pages)
- A GitHub API key (for accessing private repositories) _[Optional. Only required if you want to generate wiki from GitHub URLs]_
- Ignore file _[Optional. Only required if you want to ignore files and folders]_

## FAQs

### Q: How do I add the Gemini API key?
A: You can add the Gemini API key by setting the `GEMINI_API_KEY` environment variable in a `.env` file in the root directory of the project. The file should look like this:
```
GEMINI_API_KEY=your_api_key_here
```

### Q: How do I add the GitHub API key?
A: You can add the GitHub API key by setting the `GITHUB_AUTH_TOKEN` environment variable in a `.env` file in the root directory of the project. The file should look like this:
```
GITHUB_AUTH_TOKEN=your_api_key_here
```

### Q: How do I run the script?
A: You can run the script by executing the following command in your terminal:
```bash
python -m src --repo path/to/your/repo --output optional/path/to/output
```

### Q: How do I generate wiki pages for a specific file?
A: You can generate wiki pages for a specific file by providing the path to the file in the `--repo` parameter. The script will generate a wiki page for that file only.

**NOTE**: This doesn't work with GitHub repository URLs. The script will clone the repository and generate wiki pages for all files in that repository.

### Q: How do I generate wiki pages for all files in a directory?
A: You can generate wiki pages for all files in a directory by providing the path to the directory in the `--repo` parameter. The script will generate wiki pages for all files in that directory and its subdirectories.

### Q: How do I generate wiki pages for a git repository?
A: You can generate wiki pages for a git repository by providing the path to the repository in the `--repo` parameter. The script will clone the repository and generate wiki pages for all files in that repository.

**NOTE**: The script can only access the GitHub repository using the `GITHUB_AUTH_TOKEN`. If you don't have access to the repository, you will need to provide a personal access token with the appropriate permissions.

### Q: How do I generate wiki pages for a specific language?
A: The script is language-agnostic and will generate wiki pages for all files in the specified directory, regardless of their language. However, you can filter the files by language by modifying the script to include only the desired file extensions.

### Q: How do I exclude files and folders from the wiki generation?
A: You can exclude files and folders from the wiki generation by providing a file path to ignore file path in the `--ignore_file` parameter. The file should contain regex patterns for the files and folders to ignore.

## Want more features?
If you have any suggestions for new features or improvements, please feel free to open an issue or submit a pull request. We welcome contributions from the community!

PS: Please make sure to add tests for big modules and functions.