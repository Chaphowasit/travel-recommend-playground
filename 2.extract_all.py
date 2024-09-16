import json
import html
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

def convert_time_string(value):
    try:
        # Convert '5:30 PM' or similar formats to '17:30:00'
        return datetime.strptime(value.strip(), '%I:%M %p').time().strftime('%H:%M:%S')
    except ValueError:
        return value


# Constants for patterns and classes
LATITUDE_PATTERN = r'"latitude":(\d+\.\d+)'
LONGITUDE_PATTERN = r'"longitude":(\d+\.\d+)'
LAT_LONG_PATTERN = r"latitude%5C%5C%5C%22%3A(\d+\.\d+)%2C%5C%5C%5C%22longitude%5C%5C%5C%22%3A(\d+\.\d+)"

# Utility functions
def remove_newline_and_extra_spaces(string):
    return re.sub(r'\s+', ' ', string).replace("\n", "").strip()

def extract_lat_long(html_content):
    latitude_match = re.search(LATITUDE_PATTERN, html_content)
    longitude_match = re.search(LONGITUDE_PATTERN, html_content)

    if latitude_match and longitude_match:
        return float(latitude_match.group(1)), float(longitude_match.group(1))
    
    lat_long_match = re.search(LAT_LONG_PATTERN, html_content)
    if lat_long_match:
        return float(lat_long_match.group(1)), float(lat_long_match.group(2))
    
    return None, None

def clean_reviews(reviews):
    return [
        remove_newline_and_extra_spaces(
            re.sub(r"[^\x00-\x7F]+", "", review.text.strip())
        ) for review in reviews
    ] if reviews else None

def extract_nearby_places(soup, best_nearby_hotels):
    
    # Initialize the classification dictionary with the new fields
    if not best_nearby_hotels:
         classification_nearby = {
        "nearby_foodAndDrink1": None,
        "nearby_foodAndDrink2": None,
        "nearby_foodAndDrink3": None,
        "nearby_activity1": None,
        "nearby_activity2": None,
        "nearby_activity3": None,
    }
    else:
        classification_nearby = {
        "nearby_accommodation1": None,
        "nearby_accommodation2": None,
        "nearby_accommodation3": None,
        "nearby_foodAndDrink1": None,
        "nearby_foodAndDrink2": None,
        "nearby_foodAndDrink3": None,
        "nearby_activity1": None,
        "nearby_activity2": None,
        "nearby_activity3": None,
    }

    # First method to find nearby places
    nearby_places = soup.find_all(class_="biGQs _P fiohW ngXxk")
    if not nearby_places:
        nearby_places = soup.find_all(class_="sectionTitle")
    
    if nearby_places:
        nearby_places_text = [place.text.strip() for place in nearby_places]
        # Identify indexes for hotels, restaurants, and attractions
        try:
            index_best_nearby_hotels = nearby_places_text.index("Best nearby hotels")
            index_best_nearby_restaurants = nearby_places_text.index("Best nearby restaurants")
            index_best_nearby_attractions = nearby_places_text.index("Best nearby attractions")

            classification_nearby["nearby_accommodation1"] = nearby_places_text[index_best_nearby_hotels + 1] if index_best_nearby_hotels + 1 < index_best_nearby_restaurants else None
            classification_nearby["nearby_accommodation2"] = nearby_places_text[index_best_nearby_hotels + 2] if index_best_nearby_hotels + 2 < index_best_nearby_restaurants else None
            classification_nearby["nearby_accommodation3"] = nearby_places_text[index_best_nearby_hotels + 3] if index_best_nearby_hotels + 3 < index_best_nearby_restaurants else None

            classification_nearby["nearby_foodAndDrink1"] = nearby_places_text[index_best_nearby_restaurants + 1] if index_best_nearby_restaurants + 1 < index_best_nearby_attractions else None
            classification_nearby["nearby_foodAndDrink2"] = nearby_places_text[index_best_nearby_restaurants + 2] if index_best_nearby_restaurants + 2 < index_best_nearby_attractions else None
            classification_nearby["nearby_foodAndDrink3"] = nearby_places_text[index_best_nearby_restaurants + 3] if index_best_nearby_restaurants + 3 < index_best_nearby_attractions else None

            classification_nearby["nearby_activity1"] = nearby_places_text[index_best_nearby_attractions + 1] if index_best_nearby_attractions + 1 < len(nearby_places_text) else None
            classification_nearby["nearby_activity2"] = nearby_places_text[index_best_nearby_attractions + 2] if index_best_nearby_attractions + 2 < len(nearby_places_text) else None
            classification_nearby["nearby_activity3"] = nearby_places_text[index_best_nearby_attractions + 3] if index_best_nearby_attractions + 3 < len(nearby_places_text) else None
        except ValueError:
            pass

    # Second method if the first one didn't work or only found restaurants and attractions
    if not any([classification_nearby[f"nearby_foodAndDrink{i}"] for i in range(1, 4)]) or not any([classification_nearby[f"nearby_activity{i}"] for i in range(1, 4)]):
        nearby_places = soup.find_all(class_="xCVkR")
        if nearby_places:
            res = [place for place in nearby_places if "Restaurants" in place.text.strip()]
            attr = [place for place in nearby_places if "Attractions" in place.text.strip()]

            if res:
                res = [place.find_all(class_="o W q") for place in res]
                restaurants = [item.text.strip() for sublist in res for item in sublist if item][:3]
                for i, restaurant in enumerate(restaurants):
                    classification_nearby[f"nearby_foodAndDrink{i+1}"] = restaurant
            if attr:
                attr = [place.find_all(class_="o W q") for place in attr]
                attractions = [item.text.strip() for sublist in attr for item in sublist if item][:3]
                for i, attraction in enumerate(attractions):
                    classification_nearby[f"nearby_activity{i+1}"] = attraction

    # Third method if previous methods didn't yield results
    if not any([classification_nearby[f"nearby_foodAndDrink{i}"] for i in range(1, 4)]) or not any([classification_nearby[f"nearby_activity{i}"] for i in range(1, 4)]):
        nearby_places = soup.find_all(class_="yvHvW")
        if nearby_places:
            res = nearby_places[0].find_all(class_="biGQs _P alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU ngXxk")
            attr = nearby_places[1].find_all(class_="biGQs _P alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU ngXxk")

            restaurants = [remove_newline_and_extra_spaces(restaurant.text.strip()) for restaurant in res if restaurant.text.strip() != ""][:3]
            attractions = [remove_newline_and_extra_spaces(attraction.text.strip()) for attraction in attr if attraction.text.strip() != ""][:3]
            
            for i, restaurant in enumerate(restaurants):
                classification_nearby[f"nearby_foodAndDrink{i+1}"] = restaurant
            for i, attraction in enumerate(attractions):
                classification_nearby[f"nearby_activity{i+1}"] = attraction

    return classification_nearby



def get_next_id(existing_ids, prefix):
    # Extract numbers from IDs that match the given prefix
    ids_with_prefix = [int(id[len(prefix):]) for id in existing_ids if id.startswith(prefix)]
    if ids_with_prefix:
        next_id_num = max(ids_with_prefix) + 1
    else:
        next_id_num = 1
    return f"{prefix}{next_id_num:04d}"

def generate_id(category_name, existing_ids):
    if category_name == 'foodAndDrink_name':
        prefix = 'F'
    elif category_name == 'accommodation_name':
        prefix = 'H'
    elif category_name == 'activity_name':
        prefix = 'A'
    else:
        raise ValueError("Unknown table name")
    
    # Generate the next ID
    return get_next_id(existing_ids, prefix)

def clean_html_and_classify(json_data, name_key, desc_class, reviews_class=None, time_class=None, duration=False, best_nearby_hotels=True):
    cleaned_json = []
    
    for entry in json_data:
        url = entry.get("url", "")
        html_content = html.unescape(entry.get("html", ""))
        soup = BeautifulSoup(html_content, "html.parser")
        
        id_name = f"{name_key[:len(name_key)-len("_name")]}_id"
        classification = {}
        existing_ids = [entry.get("classification", {}).get(f"{id_name}", "") for entry in json_data if "classification" in entry]
        # Generate ID based on table name and existing IDs
        classification[id_name] = generate_id(name_key, existing_ids) if name_key else None

        # Extract title
        headings = soup.find_all(["h1", "h2", "h3"])
        classification[name_key] = headings[0].text.strip() if headings else None

        # Extract description
        paragraphs = soup.find_all(class_=desc_class)
        
        if not paragraphs:
            paragraphs = soup.find_all(class_="ui_columns")
            # find element with the "Details" text
            paragraphs = [ para for para in paragraphs if "About" in para.text.strip() and "Manage this business?" not in para.text.strip()
]
        if paragraphs:
            classification["about_and_tags"] = [
                remove_newline_and_extra_spaces(paragraph.text.strip()) for paragraph in paragraphs
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

        # Extract latitude and longitude
        latitude, longitude = extract_lat_long(html_content)
        classification["latitude"] = latitude
        classification["longitude"] = longitude

        # Set time duration or start/end times if applicable
        if type(time_class) == tuple and len(time_class) == 2:
            classification["start_time"], classification["end_time"] = convert_time_string(time_class[0]), convert_time_string(time_class[1])
        else:
            start_end_time = soup.find_all(class_=time_class)
            if start_end_time:
                time_classes = [remove_newline_and_extra_spaces(time) for time in start_end_time[0].text.split("-")]
                classification["start_time"] = convert_time_string(time_classes[0])
                classification["end_time"] = convert_time_string(time_classes[1])
            else:
                classification["start_time"] = None
                classification["end_time"] = None
      

        if duration:
            classification["duration"] = None
            duration_pattern = r"Duration:\s*.*?(\d+)"
            duration_match = re.search(duration_pattern, html_content)
            if duration_match:
                duration_int = int(duration_match.group(1))
                classification["duration"] = duration_int

        # Extract reviews
        classification["reviews"] = None
        reviews = soup.find_all(class_=reviews_class) or soup.find_all(class_="partial_entry")
        classification["reviews"] = clean_reviews(reviews)
        
        if reviews_class == "dodo":
                reviews_outer = soup.find_all(class_="JguWG")
                reviews_inner = [review.find_all(class_="yCeTE") for review in reviews_outer]
                reviews_inner_flat = [item for sublist in reviews_inner for item in sublist]  # Flatten the list

                if reviews_inner_flat:
                    classification["reviews"] = [review.text.strip() for review in reviews_inner_flat]
                    classification["reviews"] = [
                        remove_newline_and_extra_spaces(
                            re.sub(r"[^\x00-\x7F]+", "", review.text.strip())
                        )
                        for review in reviews_inner_flat
                    ]

        # Extract nearby places
        classification_nearby = extract_nearby_places(soup, best_nearby_hotels)
        classification.update(classification_nearby)
       
        entry["html"] = html_content
        entry["classification"] = classification
        cleaned_json.append(entry)

    return cleaned_json

def process_files(input_directory, output_directory, name_key, desc_class, reviews_class, time_class=None, duration=False, best_nearby_hotels=True):
    os.makedirs(output_directory, exist_ok=True)
    json_files = [f for f in os.listdir(input_directory) if f.endswith(".json")]

    for json_file in json_files:
        input_file = os.path.join(input_directory, json_file)
        output_file = os.path.join(output_directory, f"{os.path.splitext(json_file)[0]}_clean.json")

        try:
            with open(input_file, "r", encoding="utf-8") as file:
                json_data = json.load(file)

            cleaned_data = clean_html_and_classify(json_data, name_key, desc_class, reviews_class,  time_class, duration, best_nearby_hotels)
            classification_data = [entry["classification"] for entry in cleaned_data]

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(classification_data, file, indent=4, ensure_ascii=False)

            print(f"Data successfully cleaned and saved to '{output_file}'")

        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from '{input_file}': {e}")
        except Exception as ex:
            print(f"An error occurred with file '{input_file}': {ex}")

# Example usage for the different datasets
process_files("eat/prettier_json", "eat/extract_json", "foodAndDrink_name", "biGQs _P pZUbB alXOW eWlDX GzNcM ATzgx UTQMg TwpTY hmDzD", "JguWG", "biGQs _P pZUbB egaXP hmDzD", False, True)
process_files("stay/prettier_json", "stay/extract_json", "accommodation_name", "uqMDf z BGJxv YGfmd YQkjl", "orRIx Ci _a C", ("12:00 AM", "11:59 PM"), False,False)
process_files("do/prettier_json", "do/extract_json", "activity_name", "USjYi _d", "dodo" , "EFKKt",True, False)
