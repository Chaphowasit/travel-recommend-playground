import json
import html
import os
import re
from bs4 import BeautifulSoup

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
            class_="biGQs _P pZUbB alXOW eWlDX GzNcM ATzgx UTQMg TwpTY hmDzD"
        )
        if paragraphs:
            classification["about_and_tags"] = [
                para.text.strip() for para in paragraphs
            ]
        else:
            # Try to find description using regex
            description_pattern = r'"description":"(.*?)"'
            description_match = re.search(description_pattern, html_content)
            description_soup = soup.find_all(class_="SrqKb")

            if description_match:
                # Initialize as a list with the matched description
                classification["about_and_tags"] = [description_match.group(1)]

                # Append the description_soup text to the list
                for desc in description_soup:
                    classification["about_and_tags"].append(desc.text.strip())
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

        # Extract time_duration from the HTML content
        time_duration = soup.find_all(class_="biGQs _P pZUbB egaXP hmDzD")
        if time_duration:
            for time in time_duration:
                time_str = time.text.strip()
                time_str = " ".join(time_str.split())
                time_str = time_str.replace("\n - \n", " - ")
                times = time_str.split("-")
                if len(times) == 2:
                    start_time, end_time = map(str.strip, times)
                    # Add start_time and end_time to classification dictionary
                    classification["start_time"] = start_time
                    classification["end_time"] = end_time
                else:
                    classification["start_time"] = None
                    classification["end_time"] = None
        else:
            time_duration_pattern = r"\"times\":\[(.*?)\]"
            time_duration_match = re.search(time_duration_pattern, html_content)
            if time_duration_match:
                # "\"12:00 AM - 11:59 PM\"" i want to clean this string
                time_duration = time_duration_match.group(1)
                time_duration = time_duration.replace('"', "")
                times = time_duration.split("-")
                if len(times) == 2:
                    start_time, end_time = map(str.strip, times)
                    # Add start_time and end_time to classification dictionary
                    classification["start_time"] = start_time
                    classification["end_time"] = end_time
                else:
                    classification["start_time"] = None
                    classification["end_time"] = None
            else:
                classification["start_time"] = None
                classification["end_time"] = None

        # extract reviews from the HTML content
        reviews = soup.find_all(class_="JguWG")
        if reviews:
            classification["reviews"] = [review.text.strip() for review in reviews]
            classification["reviews"] = [
                re.sub(r"[^\x00-\x7F]+", "", review)
                for review in classification["reviews"]
            ]
        else:
            reviews = soup.find_all(class_="partial_entry")
            if reviews:
                classification["reviews"] = [review.text.strip() for review in reviews]
                # clear all emojis in reviews
                classification["reviews"] = [
                    re.sub(r"[^\x00-\x7F]+", "", review)
                    for review in classification["reviews"]
                ]
            else:
                classification["reviews"] = None

        # extract nearby places from the HTML content
        nearby_places = soup.find_all(class_="biGQs _P fiohW ngXxk")
        if nearby_places:
            nearby_places = [place.text.strip() for place in nearby_places]
        else:
            nearby_places = soup.find_all(class_="sectionTitle")
            if nearby_places:
                nearby_places = [place.text.strip() for place in nearby_places]

        best_nearby_hotels = []
        best_nearby_restaurants = []

        if "Best nearby hotels" in nearby_places:
            index_best_nearby_hotels = nearby_places.index("Best nearby hotels")
        if "Best nearby restaurants" in nearby_places:
            index_best_nearby_restaurants = nearby_places.index(
                "Best nearby restaurants"
            )
        if "Best nearby attractions" in nearby_places:
            index_best_nearby_attractions = nearby_places.index(
                "Best nearby attractions"
            )

        for item in nearby_places:
            if item == "Best nearby hotels":
                best_nearby_hotels = nearby_places[
                    index_best_nearby_hotels + 1 : index_best_nearby_restaurants
                ]
            if item == "Best nearby restaurants":
                best_nearby_restaurants = nearby_places[
                    index_best_nearby_restaurants + 1 : index_best_nearby_attractions
                ]
            if item == "Best nearby attractions":
                best_nearby_attractions = nearby_places[
                    index_best_nearby_attractions + 1 :
                ]

        classification["best_nearby_hotels"] = best_nearby_hotels
        classification["best_nearby_restaurants"] = best_nearby_restaurants

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