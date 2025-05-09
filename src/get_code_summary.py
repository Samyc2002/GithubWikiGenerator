from dotenv import load_dotenv
import json
import os
import subprocess
import pathlib
import time
import requests

load_dotenv()


def _sanitize_code(code: str) -> str:
    # Remove any null bytes and normalize line endings
    return code.replace("\x00", "").replace("\r\n", "\n").strip()


class CodeAnalyzer:
    def __init__(self, timeout: int = 45, max_retries: int = 3) -> None:
        self.timeout = timeout
        self.max_retries = max_retries

    def analyze_code_block(self, code: str, filename: str, retry_count: int = 0) -> str:
        code = _sanitize_code(code)
        if not code:
            return "Empty file or unreadable content"

        prompt = f"""
            You are a world class expert at code documentation. I am trying to generate documentation for the code I wrote.
            I do not want to mention any code in the documentation, but just provide a high-level overview of the code.
            
            Analyzing file: {filename}

            Below is the source code to analyze:
            {code}

            Generate a concise wiki documentation for this code file. Focus ONLY on providing the following sections:

            # Overview
            [Provide a brief 2-3 sentence description of the file's main purpose]

            # Key Features
            - [List 3-5 main features or functionalities]

            # Dependencies
            - [List main dependencies, if any]

            IMPORTANT: 
            - DO NOT include the actual code anywhere
            - Keep the response brief and wiki-friendly
            - Focus on high-level documentation
            - Use clear, non-technical language where possible
            - Limit each section to essential information only
            - DO NOT generate any section other than the ones mentioned here
        """
        try:
            # Call Gemini API to get file summary
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.environ['GEMINI_API_KEY']}",
                data=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                }
            )

            explanation = response.json()
            meaningful_content = explanation["candidates"][0]["content"]["parts"][0]["text"]
            if meaningful_content.startswith("```") and meaningful_content.endswith("```"):
                meaningful_content = "\n".join(meaningful_content.split("\n")[1:-1])

            return meaningful_content if meaningful_content else ""

        except subprocess.TimeoutExpired:
            return "Analysis timed out"
        except subprocess.CalledProcessError as e:
            if retry_count < self.max_retries:
                time.sleep(2)
                return self.analyze_code_block(code, filename, retry_count + 1)
            return "Analysis failed after multiple attempts"

    def analyze_file(self, file_path: str) -> dict:
        path = pathlib.Path(file_path)
        name = path.name

        try:
            if not path.exists():
                raise ValueError(f"File not found: {file_path}")

            if path.stat().st_size == 0:
                return {"name": name, "description": "Empty file"}

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            description = self.analyze_code_block(content, pathlib.Path(file_path).name)

            return {
                "name": name,
                "description": description or "",
            }

        except Exception as e:
            return {"name": name, "description": f"Error during analysis: {str(e)}"}
