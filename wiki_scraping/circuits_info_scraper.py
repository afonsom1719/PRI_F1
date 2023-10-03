import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import pandas as pd
import os
from multiprocessing import Pool

# Function to scrape driver data
def scrape_circuit_data(url):
    try:
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            circuit_bio_string = ""
            mw_content_text = soup.find(id="mw-content-text")
            next = mw_content_text.next
            if next is not None:
                while next.name != "h2":
                    if next.name == "p":
                        circuit_bio_string += next.text
                    next = next.next

            circuit_bio_string = circuit_bio_string.replace('\n', '')
            circuit_bio_string = re.sub(r'\[[0-9]+\]', '', circuit_bio_string)
            return circuit_bio_string
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
    return ""

# Function to print a progress bar
def print_progress_bar(iteration, total, length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(length * progress))
    spaces = ' ' * (length - len(arrow))
    print(f'\r[{arrow}{spaces}] {int(progress * 100)}%', end='', flush=True)

if __name__ == '__main__':
    # Read circuits file
    circuits = pd.read_csv('f1db_csv/circuits.csv')
    
    # Create a pool of worker processes
    pool = Pool(processes=4)  # Adjust the number of processes as needed
    
    # Use the pool to scrape driver data in parallel
    circuit_urls = circuits["url"].tolist()
    circuit_bios = []
    
    for i, result in enumerate(pool.imap_unordered(scrape_circuit_data, circuit_urls)):
        circuit_bios.append(result)
        print_progress_bar(i + 1, len(circuit_urls))
    
    print("\nComplete")
    
    # Add the scraped data to the DataFrame
    circuits["circuit_bio"] = circuit_bios
    
    # Save the updated DataFrame to a new CSV file
    circuits.to_csv('f1db_csv/circuits_op.csv', index=False)
