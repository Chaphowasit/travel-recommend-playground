import os
import json


def process_json(input_file, output_dir):
    try:
        # Read the JSON file
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Validate the data
        if not isinstance(data, list):
            raise ValueError("JSON data must be a list of records.")

        # Generate new IDs and add to data
        starting_id = 2001
        for idx, record in enumerate(data):
            new_id = f"A{starting_id + idx}"
            record["activity_id"] = new_id

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the modified JSON file
        output_file = os.path.join(output_dir, "output.json")
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print(f"Processed file saved at: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Input and output paths
input_file = "do_add300/extract_json/job-15296794-result_output1_clean.json"  # Replace with your input JSON file path
output_dir = "do_add300/extract_json/job-15296794-result_output1_clean_newid.json"  # Replace with your desired output directory

# Run the function
process_json(input_file, output_dir)
