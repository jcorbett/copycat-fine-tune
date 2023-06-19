#!/usr/bin/env python3
import os
import sys
import json
from gen_training_data import get_token_count
from helpers.local_files import (generate_jsonl_filename, 
                                 combine_jsonl_files, 
                                 get_lines, 
                                 list_files_in_dir,
                                 save_lines_to_file)
from typing import List, Tuple

def get_jsonl_token_count(jsonl_file_path: str) -> Tuple[List[dict], int]:
    token_count = 0
    json_lines  = get_lines(file_path = jsonl_file_path)
    json_dicts  = []
    for line in json_lines:
        try:
            obj          = json.loads(line)
            prompt       = obj['prompt']
            completion   = obj['completion']
            token_count += get_token_count(text=prompt + " " + completion)
            json_dicts.append(obj)
        except Exception as e:
            print(f"Error: {str(e)}")
        
    return (json_dicts, token_count)
    

def main(data_dir: str, combine_jsonl: bool = False) -> None:
    jsonl_files  = list_files_in_dir(directory = data_dir, extension = ".jsonl")
    total_tokens = 0
    json_objects = []
    for f in jsonl_files:
        json_list, token_count = get_jsonl_token_count(jsonl_file_path = os.path.join(data_dir, f))
        print(f"token count: {token_count} for file: {f}")
        total_tokens += token_count
        json_objects += json_list
    print("--------------------------")
    print(f"total tokens: {total_tokens}")

    
    if combine_jsonl:
        filename = "training_file.jsonl"
        # json_strings = []
        # for obj in json_objects:
        #     try:
        #         json_str = json.dumps(obj)
        #         json_strings.append(json_str)
        #     except Exception as e:
        #         print(f"Error combining line: {obj}, {str(e)}")
        # print(f"combined jsonl files: {len(json_strings)}")
        # save_lines_to_file(lines = json_strings, filepath = os.path.join(data_dir, filename))
        combine_jsonl_files(input_dir = data_dir, filename = filename)

        
        # filepath = os.path.join(data_dir, filename)
        # combined_count = get_jsonl_token_count(jsonl_file_path = filepath)
        # print(f"combined token count: {combined_count}")


        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_data.py <training_data_dir>")
        sys.exit(1)

    output_dir = sys.argv[1]
    main(data_dir = output_dir, combine_jsonl = True)