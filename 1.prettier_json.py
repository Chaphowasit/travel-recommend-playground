import json
from bs4 import BeautifulSoup
import os
import glob

# Specify the directory containing the .jsonl files
input_directory = "do"  # Replace with your directory path
output_directory = os.path.join(
    input_directory, "prettier_json"
)  # Output in a subdirectory

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Get all .jsonl files in the directory
jsonl_files = glob.glob(os.path.join(input_directory, "*.jsonl"))

# Process each .jsonl file
for input_file in jsonl_files:
    # Read the JSONL file
    with open(input_file, "r", encoding="utf-8") as f_in:
        json_data = [json.loads(line) for line in f_in]

    # Reformat each JSON object and prettify the HTML
    for entry in json_data:
        # Rename the keys
        entry["url"] = entry.pop("input")
        entry["html"] = entry.pop("result")

        # Use BeautifulSoup to prettify the HTML
        soup = BeautifulSoup(entry["html"], "html.parser")
        entry["html"] = soup.prettify()

    # Determine the base output file name
    base_name = os.path.basename(input_file).replace(".jsonl", "_output")

    # Determine the next available number for the output file
    file_number = 1
    while os.path.exists(
        os.path.join(output_directory, f"{base_name}{file_number}.json")
    ):
        file_number += 1

    # Construct the output file path with the incremented number
    output_file = os.path.join(output_directory, f"{base_name}{file_number}.json")

    # Write the reformatted and prettified data to a JSON file
    with open(output_file, "w", encoding="utf-8") as f_out:
        json.dump(json_data, f_out, indent=4)

    print(f"Reformatted and prettified data written to {output_file}")
