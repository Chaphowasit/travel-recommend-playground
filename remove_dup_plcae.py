import os
import json

# Define the input directories and corresponding output directories
input_output_dirs = {
    "do_add300/extract_json": "do_add300/extract_json_no_dup",
    # "stay/extract_json_image": "stay/extract_json_no_dup",
}


# Function to remove duplicates across all files
def remove_duplicates_across_files(data, keys):
    seen = set()
    filtered_data = []
    for obj in data:
        # Create a tuple of values for the keys
        identifier = tuple(obj.get(key) for key in keys if key in obj)
        if identifier not in seen:
            seen.add(identifier)
            filtered_data.append(obj)
    return filtered_data


# Process each input directory and save results to corresponding output directory
for input_dir, output_dir in input_output_dirs.items():
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    all_data = []  # To store combined data from all files

    # Read and combine data from all files in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".json"):
            input_file_path = os.path.join(input_dir, file_name)

            # Read JSON file
            with open(input_file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    if isinstance(data, list) and all(
                        isinstance(item, dict) for item in data
                    ):
                        all_data.extend(data)
                except json.JSONDecodeError:
                    print(f"Failed to parse {file_name} from {input_dir}. Skipping.")
                    continue

    # Remove duplicates across all combined data
    unique_data = remove_duplicates_across_files(
        all_data, ["activity_name", "accommodation_name"]
    )

    # Write the filtered unique data back into respective files in the output directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".json"):
            output_file_path = os.path.join(output_dir, file_name)

            # Calculate the number of entries to assign to this file
            if len(unique_data) > 0:
                num_entries = min(
                    len(unique_data), len(all_data) // len(os.listdir(input_dir))
                )
                file_data = unique_data[:num_entries]  # Assign entries to this file
                unique_data = unique_data[num_entries:]  # Remove assigned entries

                # Write data to the output file
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    json.dump(file_data, output_file, indent=4)

print(
    "Processing complete. Deduplicated files are saved in their respective output directories."
)
