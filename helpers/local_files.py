import os
import json
import uuid
from typing import List

# save text to a new file
def save_to_file(*, text: str, filepath: str) -> None:
    with open(filepath, 'w') as f:
        f.write(text)

def save_lines_to_file(*, lines: List[str], filepath: str, add_newline: bool = False) -> None:
    newline = "\n" if add_newline else ""
    with open(filepath, 'w') as f:
        # Iterate through the string array and write each item to the file as a new line
        for item in lines:
            f.writelines(item + newline)
    
# list markdown files in directory
def list_files_in_dir(*, directory: str, extension: str = ".md") -> List[str]:
    files = []
    for file in os.listdir(directory):
        if file.lower().endswith(extension):
            files.append(file)
    return files

# generate a filename for a markdown file
def generate_markdown_filename(base_dir: str) -> str:
    return os.path.join(base_dir, f"blog_markdown-{uuid.uuid4()}.md")

# generate a filename for a jsonl file
def generate_jsonl_filename(markdown_name: str) -> str:
    return markdown_name.replace(".md", ".jsonl")

# combine all jsonl files in a directory into one jsonl file
def combine_jsonl_files(input_dir: str, filename: str) -> None:
    final_jsonl_file = os.path.join(input_dir, filename)
    
    files = list_files_in_dir(directory = input_dir, extension = ".jsonl")
    print(f"files: {files}")
    lines = []
    for file in files:
        file = os.path.join(input_dir, file)
        print(f"append jsonl: {file}")
        lines += get_lines(file)
        # append_jsonl_file(input_filepath = file, output_filepath = final_jsonl_file)

    json_lines = []
    for line in lines:
        try:
            obj      = json.loads(line)
            json_str = json.dumps(obj)
            json_lines.append(json_str)
            print(json_str)
        except Exception as e:
            print(f"Error combining line: {line}, {str(e)}")
            
    save_lines_to_file(lines = lines, filepath = final_jsonl_file)
    print(f"total lines: {len(lines)}")


# open one of our markdown files and parse it into a dictionary
def get_lines(file_path: str) -> List[str]:
    lines = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return lines