import os
import json


# Function to split reviews into individual entries
def split_reviews_individually(data):
    # Extract the reviews from the data
    reviews = data.get("reviews", [])
    if not isinstance(reviews, list):
        print(
            f"Warning: 'reviews' is not a list for accommodation_id {data.get('accommodation_id')}. Skipping this entry."
        )
        return []
    # Create a new entry for each review while keeping other fields unchanged
    individual_entries = []
    for review in reviews:
        # Create a copy of the original data
        new_entry = data.copy()
        # Replace the reviews field with the current single review
        new_entry["reviews"] = [review]
        individual_entries.append(new_entry)

    return individual_entries


# Directory where your JSON files are located
input_directory = "do/extract_json_version2_noDup_image/"
output_directory = "do/extract_json_1review/"

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Loop through all files in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".json"):
        # Construct full file path
        file_path = os.path.join(input_directory, filename)

        # Open and load the JSON data
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Process each entry in the JSON file
        if isinstance(data, list):
            # If data is a list of entries
            all_individual_entries = []
            for entry in data:
                # Split each review into individual entries
                individual_entries = split_reviews_individually(entry)
                all_individual_entries.extend(individual_entries)
        else:
            # If data is a single entry (not a list)
            all_individual_entries = split_reviews_individually(data)

        # Write the individual review data into a new JSON file
        output_file_path = os.path.join(output_directory, f"split_{filename}")
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            json.dump(all_individual_entries, output_file, indent=4, ensure_ascii=False)

        print(f"Processed and saved individual reviews to {output_file_path}")
