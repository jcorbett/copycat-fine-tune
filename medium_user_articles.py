#!/usr/bin/env python3
import sys
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from typing import List

# format medium url
def get_medium_url(username: str) -> str:
    return f"https://medium.com/@{username}"

# parse html for article links
def parse_html_for_article_links(*, html: str, username: str) -> List[str]:
    base_url = get_medium_url(username = username)
    soup     = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')

    # find all links on the page
    links = [] # articles.find_all('a')

    # print(articles)
    for article in articles:
        link = article.find('a')
        for link in article.find_all('a'):
            if link and link['href'][0] == '/' and link['href'] not in links:
                links.append(link['href'])       

    links = [f"https://medium.com/{link}]" for link in links]
    return links

# get medium page (html) with requests
def get_html_with_requests(username: str) -> str:
    url      = get_medium_url(username)
    response = requests.get(url)
    return response.text

# get medium page (html) with selenium. This is needed to scroll to the bottom of the page
# warning, this launches a browser window
def get_html_with_selenium(username) -> str:
    url = get_medium_url(username)
    # Create a new instance of the Chrome driver (make sure to have the chromedriver in your PATH)
    driver = webdriver.Chrome()
    # Go to the page
    driver.get(url)
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # After scrolling to the bottom of the page, get the page source
    html = driver.page_source

    # close the browser
    driver.quit()

    return html

# get all article links for a medium user
def get_links_for_user(username: str, use_selenium_for_scrolling: bool = False) -> List[str]:
    html : str = ""
    if use_selenium_for_scrolling:
        html  = get_html_with_selenium(username)
    else:
        html  = get_html_with_requests(username)
        
    links = parse_html_for_article_links(html= html, username= username)    
    return links


if __name__ == "__main__":
    username = sys.argv[1]
    links = get_links_for_user(username, True)
    for link in links:
        print(link)