import os
import json
import time
import requests
import simple_image_download.simple_image_download as simp
from urllib3.exceptions import LocationParseError


# Function to find all JSON files in a directory
def find_json_files(directory):
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files


def search_images_with_retry(downloader, search_query, max_attempts=3, limit=5):
    """
    Search for image URLs with retries and handle DNS/connection issues more robustly.
    """
    attempts = 0
    urls_to_try = []

    while attempts < max_attempts:
        try:
            # Attempt to retrieve URLs for the query
            downloader.search_urls(search_query, limit=limit, verbose=False)
            urls_to_try = downloader.get_urls()
            break  # Exit loop if URLs are successfully retrieved
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempts + 1} to search URLs failed: {e}. Retrying...")
            attempts += 1
            time.sleep(2)  # Wait before retrying search

    # Try each URL from the results
    for url in urls_to_try:
        if "gstatic" in url:  # Exclude unwanted domains
            continue

        for attempt in range(max_attempts):
            try:
                print(f"Trying URL: {url}")
                response = requests.head(url, timeout=10)  # Check URL validity
                if response.status_code == 200:
                    return url  # Return first valid URL
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} for URL {url} failed: {e}. Retrying...")
                time.sleep(2)  # Retry same URL

    print(f"Failed to retrieve any valid image URL for query: {search_query}")
    return None  # Return None if all URLs fail


# Incorporate the updated function into your JSON processing
def process_json_files(json_files, output_directory):
    my_downloader = simp.Downloader()  # Initialize downloader

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if data is a list
        if isinstance(data, list):
            for entry in data:  # Loop through each dictionary in the list
                if "activity_name" in entry:
                    # Remove spaces from activity name and use it for search
                    search_query = entry["activity_name"].replace(" ", "")
                    print(f"Searching for: {search_query}")

                    try:
                        # Search for image URLs with retry and fallback logic
                        image_url = search_images_with_retry(
                            my_downloader, search_query
                        )
                        print(f"Found Image URL: {image_url}")

                        # Add the valid URL (if found) to the entry
                        if image_url:
                            entry["image_url"] = image_url
                        else:
                            entry["image_url"] = None
                    except LocationParseError as e:
                        print(f"Skipping activity due to URL parsing error: {e}")
                        continue  # Skip this activity and move on

                    except Exception as e:
                        print(
                            f"An unexpected error occurred: {e}. Skipping this entry."
                        )
                        continue  # Skip this activity and move on

        # Save the modified JSON file to a new directory
        os.makedirs(
            output_directory, exist_ok=True
        )  # Create output directory if it doesn't exist
        output_file_path = os.path.join(output_directory, os.path.basename(json_file))
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(
                data, f, indent=4, ensure_ascii=False
            )  # Preserve Unicode characters


# Main script
input_directory = (
    "do_add300/extract_json_no_dup"  # Replace with your directory containing JSON files
)
output_directory = (
    "do_add300/extract_json_image"  # Replace with your desired output directory
)

# Find all JSON files in the directory
json_files = find_json_files(input_directory)

# Process each JSON file and add image URL
process_json_files(json_files, output_directory)

print("Processing complete! Modified JSON files saved in:", output_directory)
