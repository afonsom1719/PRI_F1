import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import pandas as pd
import os
from multiprocessing import Pool

# Function to scrape driver data
def scrape_constructor_data(url):
    try:
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            constructor_bio_string = ""
            mw_content_text = soup.find(id="mw-content-text")
            next = mw_content_text.next
            if next is not None:
                while next.name != "h2":
                    if next.name == "p":
                        constructor_bio_string += next.text
                    next = next.next

            constructor_bio_string = constructor_bio_string.replace('\n', '')
            constructor_bio_string = re.sub(r'\[[0-9]+\]', '', constructor_bio_string)
            return constructor_bio_string
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
    return " "

# Function to print a progress bar
def print_progress_bar(iteration, total, length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(length * progress))
    spaces = ' ' * (length - len(arrow))
    print(f'\r[{arrow}{spaces}] {int(progress * 100)}%', end='', flush=True)

if __name__ == '__main__':
    # Read constructors file
    constructors = pd.read_csv('f1db_csv/constructors.csv')
    
    # Create a pool of worker processes
    pool = Pool(processes=4)  # Adjust the number of processes as needed
    
    # Use the pool to scrape driver data in parallel
    constructor_urls = constructors["url"].tolist()
    constructor_bios = []
    
    for i, result in enumerate(pool.imap(scrape_constructor_data, constructor_urls)):
        constructor_bios.append(result)
        print_progress_bar(i + 1, len(constructor_urls))
    
    print("\nComplete")
    
    # Add the scraped data to the DataFrame
    constructors["constructor_bio"] = constructor_bios
    
    # Save the updated DataFrame to a new CSV file
    constructors.to_csv('f1db_csv/constructors_info.csv', index=False)
