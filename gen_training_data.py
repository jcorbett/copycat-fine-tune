#!/usr/bin/env python3
import os
import sys
import subprocess
from dotenv import load_dotenv
from typing import List
import tiktoken
import re
import json
import spacy
from gen_prompts import format_prompt
from helpers.local_files import save_to_file, list_files_in_dir, get_lines

MAX_TOKEN=1000
SENTENCE_REGEX=r'(?<=[.!?])\s+'
PARAGRAPH_REGEX=r'\n+'

load_dotenv() # take environment variables from .env.

# Load the English model in SpaCy
nlp = spacy.load('en_core_web_sm')

def get_token_count(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

def split_text_into_chunks(content, regex: str = PARAGRAPH_REGEX, separator: str = "\n") -> List[str]:
    paragraphs     = re.split(regex, content)  # split content into paragraphs
    chunks         = []
    current_chunk  = ""
    current_tokens = 0

    for paragraph in paragraphs:
        paragraph_tokens = get_token_count(paragraph)

        # if single paragraph is too long, split into sentences
        if paragraph_tokens > MAX_TOKEN:
            if regex == SENTENCE_REGEX:
                print(f"Warning: a single sentence is longer than {MAX_TOKEN} tokens. It will be skipped.")
            else:
                sentence_chunks = split_text_into_chunks(paragraph, regex=r'(?<=[.!?])\s+', separator=" ")
                chunks.extend(sentence_chunks)
        else:
            if current_tokens + paragraph_tokens > MAX_TOKEN:
                # If adding this paragraph would exceed the limit, start a new chunk.
                chunks.append(current_chunk)
                current_chunk = paragraph
                current_tokens = paragraph_tokens
            else:
                # Otherwise, add this paragraph to the current chunk.
                current_chunk = current_chunk + separator + paragraph if current_chunk else paragraph
                current_tokens += paragraph_tokens

    # Add the final chunk (if it's non-empty)
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def parse_lines(lines: List[str]) -> dict:
    data          = {}
    current_key   = None
    current_value = ''
    i             = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if i < len(lines) - 1:  # If this is not the last line
            next_line = lines[i + 1].strip()
            if next_line.startswith('===') or next_line.startswith('---'):  # If the next line is a divider, this line is a key
                if current_key is not None:  # If there's a current key, save it with its value
                    data[current_key] = current_value.strip()
                    current_value = ''  # Reset the value
                current_key = line
                i += 2  # Skip the divider line
            else:  # If the next line is not a divider, this line is part of the value
                current_value += line + '\n'
                i += 1
        else:  # If this is the last line, it's part of the value
            current_value += line
            i += 1

    # Don't forget to add the last key-value pair to the dictionary
    if current_key is not None:
        data[current_key] = current_value.strip()

    return data

# open one of our markdown files and parse it into a dictionary
def parse_file(file_path: str) -> dict:
    lines = get_lines(file_path)
    return parse_lines(lines)


def create_prompt_completion_pairs_from_sentences(text: str, style_only: bool = True) -> List[str]:
    # Parse the text using SpaCy
    doc = nlp(text)

    # Split the text into sentences
    sentences = list(doc.sents)

    # Create prompt-completion pairs
    pairs = []
    for i in range(len(sentences) - 1):
        if style_only:
            pairs.append(format_prompt("", sentences[i].text))
        else:
            pairs.append(format_prompt(sentences[i].text, sentences[i + 1].text))
    return pairs


def main(input_dir, output_file):
    print(f"Input dir: {input_dir}")
    print(f"Output file: {output_file}")
    md_files = list_files_in_dir(directory=input_dir, extension=".md")
    print(md_files)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python myfile.py <input_dir> <output_file>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    main(input_dir, output_file)