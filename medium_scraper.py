#!/usr/bin/env python3

from dotenv import load_dotenv
import os
import re
import sys
import uuid
import requests
from bs4 import BeautifulSoup
import markdownify
from helpers.local_files import save_to_file, list_files_in_dir
from typing import Optional

load_dotenv() # take environment variables from .env.

# call node script that scrapes medium article
def medium_to_markdown(*, url: str) ->Optional[str]:
    response = requests.get(url)
    if response.url != url:
        print("Final URL after redirects:", response.url)
        url = response.url

    soup          = BeautifulSoup(response.text, 'html.parser')
    article_tag   = soup.find('article')
    if article_tag is not None:
        article_html   = str(article_tag)
        markdown_text  = markdownify.markdownify(article_html)
        clean_markdown = re.sub(r'(?<====).*?Share', '', markdown_text, flags=re.DOTALL)
        return clean_markdown
    else:
        print(f"ERROR: Could not find article tag in url: {url}")
        # print(soup.prettify())

# take url arg and save a blog to markdown in output_dir
def main(*, url: str, output_dir: str) -> None:
    print(f"scraping article: {url}")
    output_file = os.path.join(output_dir, f"blog_markdown-{uuid.uuid4()}.md")
    full_path   = os.path.abspath(output_file)
    print(f"saving to: {full_path}")

    # scrape, convert and save medium article to markdown
    content = medium_to_markdown(url= url)
    if content is not None:
        save_to_file(text = content, filepath = full_path)
        print("successfully saved markdown file")
    else:
        print(f"ERROR: no content returned from medium_to_markdown from url:{url}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python medium_scraper.py <url> <output_dir>")
        sys.exit(1)

    medium_url = sys.argv[1]
    output_dir = sys.argv[2]
    main(url = medium_url, output_dir = output_dir)
