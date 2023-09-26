# Imports
import requests
from bs4 import BeautifulSoup
import re
import json

#generate a list with all numbers from 1990 to 2022
years = list(range(2000, 2023))
season_prefix = "https://en.wikipedia.org/wiki/"
season_postfix = "_Formula_One_World_Championship"

data = {}

for year in years:
    season_wikilink = season_prefix + str(year) + season_postfix
    season_page = requests.get(season_wikilink)
    print(year)
    #print(season_page.status_code)
    season_soup = BeautifulSoup(season_page.content, 'html.parser')
    driver_changes = season_soup.find(id="Driver_changes")
    #find next sibling
    if driver_changes is not None:
        #find parent element
        h2_driverchange = driver_changes.parent
        print(driver_changes.text)
        #find all elements after the present element and before the next h2
        driverchange_tags = []
        next = h2_driverchange.nextSibling
        while next.name != "h2":
            driverchange_tags.append(next.text)
            next = next.nextSibling
        #for each tag in regchange_tags, remove if is '\n'
        driverchange_tags = [tag for tag in driverchange_tags if tag != '\n']
        #for each element in regchange_tags, remove parts that match [number]
        driverchange_tags = [re.sub(r'\[[0-9]+\]', '', tag) for tag in driverchange_tags]
        #For each element, if the string includes \n, split it and add the elements to the list
        driverchange_tags = [tag.split('\n') for tag in driverchange_tags]
        #convert list of lists to list
        driverchange_tags = [item for sublist in driverchange_tags for item in sublist]
        #remove empty strings
        driverchange_tags = [tag for tag in driverchange_tags if tag != '']

        data[str(year)] = {"Driver changes": driverchange_tags}
        print(driverchange_tags)
    else:
        print("No driver changes")
        data[str(year)] = {"Driver changes": "None relevant"}
    print("--------------------")

with open ("f1_driver_changes.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Data exported to f1_driver_changes.json")