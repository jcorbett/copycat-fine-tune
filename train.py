import sys
import os
import uuid
from medium_user_articles import get_links_for_user
from medium_scraper import medium_to_markdown, list_files_in_dir, save_to_file
from gen_training_data import parse_lines, split_text_into_chunks, create_prompt_completion_pairs_from_sentences
from gen_prompts import generate_prompts, format_prompt
from concurrent.futures import ThreadPoolExecutor
from helpers.local_files import (combine_jsonl_files, 
                                 generate_jsonl_filename, 
                                 generate_markdown_filename,
                                 save_to_file,
                                 save_lines_to_file,
                                 list_files_in_dir
                                )

# 1. get all article links for a user
# 2. scrape all articles for a user and save to markdown
# 3. convert markdown to subject/paragraph pairs
# 3. generate prompt pairs for each article using subject/paragraph pairs
# 4. combine prompt pairs into a single prompt file
# 5. call openai api to train new model
def main(username : str, data_dir : str, sentence_parsing : bool = True) -> None:
    base_dir = os.path.abspath(data_dir)
    
    # Create the directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    # 1. get all article links for a user (use selenium_for_scrolling if you want to get more than the top 8ish articles)
    links = get_links_for_user(username = username, use_selenium_for_scrolling=False) 
    print(links)
    
    # 2. scrape all articles for a user and save to markdown
    for link in links:
        print(f"scraping article: {link}")
        # convert content from article url into markdown
        content = medium_to_markdown(url= link)
        if content is None:
            print(f"ERROR: no content returned from medium_to_markdown from url: {link}")
            continue

        # save markdown content to file for later use (if nec)
        file_path = generate_markdown_filename(base_dir = base_dir)
        print(f"base: {base_dir}, saving to: {file_path}")
        save_to_file(text = content, filepath = file_path)

        # jsonl_lines will be lines of jsonl formatted text
        jsonl_lines = []
        
        # 3. convert markdown to subject/paragraph pairs or prompt pairs
        if sentence_parsing: # use sentence parsing
            print("sentence parsing")
            jsonl_lines = create_prompt_completion_pairs_from_sentences(text = content)

        else: # use chatgpt to create prompt pairs
            print("chatgpt parsing")
            
            # parse content
            article_dict = parse_lines(content.splitlines())
            print(f"article_dict length: {len(article_dict.items())}")

            # loop through the dictionary and split the text into chunks
            for key, value in article_dict.items():
                article_chunks = split_text_into_chunks(value)
                print(f"len article_chunks: {len(article_chunks)}")
                
                # loop through the chunks and generate prompts
                for chunk in article_chunks:
                    new_contents = key + "\n" + chunk
                    # Use ThreadPoolExecutor to process chunks in parallel
                    # with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                        # prompt_lines = list(executor.map(generate_prompts, new_contents))
                    print("prompt:")
                    prompt_lines = generate_prompts(new_contents)
                    if prompt_lines is not None:
                        for prompt in prompt_lines:
                            if prompt != "":
                                jsonl_lines.append(format_prompt(prompt, new_contents))
                    # install blank line between prompts for generator
                    jsonl_lines.append(format_prompt("", chunk))
                    print("threads complete")

        # 4. combine prompt pairs into a single jsonl prompt file for that article
        jsonl_filename = generate_jsonl_filename(file_path)
        save_lines_to_file(lines=jsonl_lines, filepath=jsonl_filename, add_newline=True)
        print(f"saved {len(jsonl_lines)} lines to: {jsonl_filename}")

    print("-----")
    print("combine all jsonl files")
    print("-----")
    combine_jsonl_files(input_dir = base_dir, filename = f"{username}.jsonl")
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python train.py <medium_username> <training_data_dir>")
        sys.exit(1)

    username   = sys.argv[1]
    output_dir = sys.argv[2]
    main(username = username, data_dir = output_dir, sentence_parsing = True)