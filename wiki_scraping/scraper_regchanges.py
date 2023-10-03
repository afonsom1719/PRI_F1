# Imports
import requests
from bs4 import BeautifulSoup
import re
import json

# Get URL
page = requests.get("https://en.wikipedia.org/wiki/2021_Formula_One_World_Championship")

# Check status code
#print(page.status_code)

# Check page content
#print(page.content)

# Scrape the page
#soup = BeautifulSoup(page.content, 'html.parser')

# Display the scraped data
#print(soup.prettify())

#generate a list with all numbers from 1990 to 2022
years = list(range(1990, 2023))
season_prefix = "https://en.wikipedia.org/wiki/"
season_postfix = "_Formula_One_World_Championship"

data = {}

for year in years:
    season_wikilink = season_prefix + str(year) + season_postfix
    season_page = requests.get(season_wikilink)
    print(year)
    #print(season_page.status_code)
    season_soup = BeautifulSoup(season_page.content, 'html.parser')
    reg_changes = season_soup.find(id="Regulation_changes")
    #find next sibling
    if reg_changes is not None:
        #find parent element
        h2_regchange = reg_changes.parent
        print(reg_changes.text)
        #find all elements after the present element and before the next h2
        regchange_tags = []
        next = h2_regchange.nextSibling
        while next.name != "h2":
            regchange_tags.append(next.text)
            next = next.nextSibling
        #for each tag in regchange_tags, remove if is '\n'
        regchange_tags = [tag for tag in regchange_tags if tag != '\n']
        #for each element in regchange_tags, remove parts that match [number]
        regchange_tags = [re.sub(r'\[[0-9]+\]', '', tag) for tag in regchange_tags]
        #For each element, if the string includes \n, split it and add the elements to the list
        regchange_tags = [tag.split('\n') for tag in regchange_tags]
        #convert list of lists to list
        regchange_tags = [item for sublist in regchange_tags for item in sublist]
        #remove empty strings
        regchange_tags = [tag for tag in regchange_tags if tag != '']

        data[str(year)] = {"Regulation changes": regchange_tags}
        print(regchange_tags)
    else:
        print("No relevant regulation changes")
        data[str(year)] = {"Regulation changes": "None relevant"}
    print("--------------------")

with open ("f1_regulation_changes.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Data exported to f1_regulation_changes.json")