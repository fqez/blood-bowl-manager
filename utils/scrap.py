import json
import re

import requests
from bs4 import BeautifulSoup


def extract_data(soup):
    # Find all the h3 elements
    h3_elements = soup.find_all("h3")

    # Process the h3 and p elements
    data = []
    for h3 in h3_elements:
        # Get the next sibling elements until the next h3
        siblings = h3.find_next_siblings()

        # Initialize variables to store the extracted text
        name = h3.text.strip()
        family = ""
        description = ""

        # Iterate over the sibling elements
        for sibling in siblings:
            # Check if the sibling is an h3 element
            if sibling.name == "h3":
                break

            # Check if the sibling is a p element or a list element
            if sibling.name == "p" or sibling.name == "ul":
                # Extract the text from the sibling element
                text = sibling.text.strip()

                # Check if the sibling is a list element
                if sibling.name == "ul":
                    # If it's a list, convert it to a string
                    text = " ".join([li.text.strip() for li in sibling.find_all("li")])

                    # If there is already a description, add a new line before the list
                    if description:
                        description += "\n"

                # Check if the sibling is the first p element
                if sibling.name == "p" and not family:
                    # Assign the text to the family variable
                    family = text.strip("()")
                    if family == "Mutations":
                        family = "Mutation"

                # Append the text to the description
                description += text + " "

        # Create a dictionary object
        skill = {"name": name, "family": family, "description": description.strip()}

        # Append the skill dictionary to the data list
        data.append(skill)

    return remove_first_parenthesis_word(data)


def remove_first_parenthesis_word(data):
    modified_data = []
    for idx, item in enumerate(data):
        # item["id"] = f"{idx:03d}"
        description = item["description"]
        # Using regular expression to remove the first occurrence of a word in parentheses
        modified_description = re.sub(r"\(\w+\)\s*", "", description, count=1)
        item["description"] = modified_description
        modified_data.append(item)
    return modified_data


def transform_object(obj):
    return {
        "id": f"perk-{'-'.join(obj['name'].lower().split(' '))}",
        "name": {"en": obj["name"], "es": obj["name_es"]},
        "family": obj["family"],
        "description": {"en": obj["description"], "es": obj["description_es"]},
    }


english_url = "https://nufflezone.com/en/blood-bowl-skills-traits/"

response = requests.get(english_url)
soup = BeautifulSoup(response.text, "html.parser")
data = extract_data(soup)


spanish_url = "https://nufflezone.com/habilidades-blood-bowl/"
response2 = requests.get(spanish_url)
soup2 = BeautifulSoup(response2.text, "html.parser")
data2 = extract_data(soup2)


dataa = []
# Update the data dictionary with the descriptions from data2
for item2 in data2:
    family = item2["family"]
    description = item2["description"]

    # Find the matching skill in data1 and update its description
    for item1 in data:
        if item1["name"] == family:
            item1["description_es"] = description
            item1["name_es"] = item2["name"]
            dataa.append(transform_object(item1))
            break


with open("perks.json", "w", encoding="utf-8") as file:
    json.dump(dataa, file, ensure_ascii=False, indent=4)

# Step 2 and 3: Group items by the 'family' field
grouped_by_family = {}
for item in dataa:
    family = item["family"]
    if family not in grouped_by_family:
        grouped_by_family[family] = []
    grouped_by_family[family].append(item)

# Step 4: Save the grouped data into a single JSON file
with open("grouped_by_family.json", "w") as file:
    json.dump(grouped_by_family, file, indent=4)
