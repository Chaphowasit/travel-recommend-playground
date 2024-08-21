import json
import html
import os
import re
from bs4 import BeautifulSoup

def remove_newline_and_extra_spaces_from_string(string):
    # Replace multiple spaces with a single space
    string = re.sub(r'\s+', ' ', string)
    # Remove all newline characters
    string = string.replace("\n", "")
    return string.strip() 


def clean_html_and_classify(json_data):
    cleaned_json = []
    for entry in json_data:
        url = entry.get("url", "")
        html_content = entry.get("html", "")
        cleaned_html = html.unescape(html_content)
        soup = BeautifulSoup(cleaned_html, "html.parser")
        classification = {}

        # Extract title and description from the HTML content
        headings = soup.find_all(["h1", "h2", "h3"])
        if headings:
            classification["accommodation_name"] = [
                heading.text.strip() for heading in headings
            ][0]

        # Extract description from the HTML content
        paragraphs = soup.find_all(
            class_="uqMDf z BGJxv YGfmd YQkjl"
        )
        if paragraphs:
            classification["about_and_tags"] = [
                remove_newline_and_extra_spaces_from_string(paragraph.text.strip())
                for paragraph in paragraphs
            ]
        else:
            classification["about_and_tags"] = None

        # Extract address from the HTML content
        latitude = None
        longitude = None
        latitude_pattern = r'"latitude":(\d+\.\d+)'
        longitude_pattern = r'"longitude":(\d+\.\d+)'

        # Find latitude and longitude using regex
        latitude_match = re.search(latitude_pattern, html_content)
        longitude_match = re.search(longitude_pattern, html_content)

        if latitude_match and longitude_match:
            latitude = float(latitude_match.group(1))
            longitude = float(longitude_match.group(1))
        else:
            latitude_longitude_pattern = r"latitude%5C%5C%5C%22%3A(\d+\.\d+)%2C%5C%5C%5C%22longitude%5C%5C%5C%22%3A(\d+\.\d+)"
            latitude_longitude_match = re.search(
                latitude_longitude_pattern, html_content
            )
            if latitude_longitude_match:
                latitude = float(latitude_longitude_match.group(1))
                longitude = float(latitude_longitude_match.group(2))

        classification["latitude"] = latitude
        classification["longitude"] = longitude

        # start_time and end_time = 00:00 AM - 11:59 PM
        classification["start_time"] = "00:00 AM"
        classification["end_time"] = "11:59 PM"
      
        # extract reviews from the HTML content
        reviews = soup.find_all(class_="orRIx Ci _a C")
        if reviews:
            classification["reviews"] = [review.text.strip() for review in reviews]
            classification["reviews"] = [
                    remove_newline_and_extra_spaces_from_string(
                        re.sub(r"[^\x00-\x7F]+", "", review.text.strip())
                    )
                    for review in reviews
                ]
        else:
            reviews = soup.find_all(class_="partial_entry")
            if reviews:
                # Extract the text, strip whitespace, remove emojis, and clear spaces and newlines
                classification["reviews"] = [
                    remove_newline_and_extra_spaces_from_string(
                        re.sub(r"[^\x00-\x7F]+", "", review.text.strip())
                    )
                    for review in reviews
                ]
            else:
                classification["reviews"] = None

        # extract nearby places from the HTML content
        nearby_places = soup.find_all(class_="xCVkR")
        if nearby_places:
            # Find text in the nearby places that contain "Restaurants" or "Attractions"
            res = [place for place in nearby_places if "Restaurants" in place.text.strip()]
            attr = [place for place in nearby_places if "Attractions" in place.text.strip()]

            # Extract relevant information if 'res' or 'attr' is found
            if res:
                res = [place.find_all(class_="o W q") for place in res]
            if attr:
                attr = [place.find_all(class_="o W q") for place in attr]

            # Extract and clean text from the found elements
            best_nearby_restaurants = [item.text.strip() for sublist in res for item in sublist if item]
            best_nearby_attractions = [item.text.strip() for sublist in attr for item in sublist if item]

            # Store the results in the classification dictionary
            classification["best_nearby_restaurants"] = best_nearby_restaurants
            classification["best_nearby_attractions"] = best_nearby_attractions

        entry["html"] = cleaned_html
        entry["classification"] = classification
        cleaned_json.append(entry)

    return cleaned_json


input_directory = "stay/prettier_json"
output_directory = "stay/extract_json"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Get a list of all .json files in the input directory
json_files = [f for f in os.listdir(input_directory) if f.endswith(".json")]

# Process each file
for json_file in json_files:
    input_file = os.path.join(input_directory, json_file)
    output_file = os.path.join(output_directory, f"{os.path.splitext(json_file)[0]}_clean.json")

    try:
        # Read the input JSON file
        with open(input_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        # Clean HTML content and classify within each object
        cleaned_data = clean_html_and_classify(json_data)
        classification_data = [entry["classification"] for entry in cleaned_data]

        # Save to a structured JSON file
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(classification_data, file, indent=4, ensure_ascii=False)

        print(f"Data has been successfully cleaned and saved to '{output_file}'")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{input_file}': {e}")
    except Exception as ex:
        print(f"An error occurred with file '{input_file}': {ex}")