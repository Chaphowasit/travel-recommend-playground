import json
import math
import os
import random
import pymysql
from dotenv import load_dotenv
import requests
import pandas as pd  # Import pandas for DataFrame support

load_dotenv()  # Load environment variables from .env file

# Load the activities and accommodations data from all JSON files in the specified directories
activities_json = []
accommodations_json = []

# Specify the directories containing the JSON files
do_json_directory = "./do/extract_json"
stay_json_directory = "./stay/extract_json"


# Function to load JSON files from a given directory
def load_json_files_from_directory(directory, accommodation=False):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):  # Check if the file is a JSON file
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                if accommodation:
                    data.extend(
                        json_data
                    )  # Assuming json_data is a list of accommodations
                else:
                    data.extend(json_data)  # Assuming json_data is a list of activities
    return data


# Load activities and accommodations from their respective directories
activities_json.extend(
    load_json_files_from_directory(do_json_directory, accommodation=False)
)
accommodations_json.extend(
    load_json_files_from_directory(stay_json_directory, accommodation=True)
)

# Filter out locations with non-null latitude and longitude
allowed_ids = {
    "H0021",  # Accommodation ID
    "A0423",
    "A0153",
    "A0155",
    "A0512",
    "A0527",
    "A0444",
    "A0002",
    "A0238",
    "A0055",
    "A0815",
    "A0809",
    "A0234",
}

# Combine valid activities and accommodations
valid_locations = []

# Process activities
valid_locations.extend(
    [
        {
            "activity_id": activity["activity_id"],  # Use 'id' from activities
            "activity_name": activity["activity_name"],
            "latitude": activity["latitude"],
            "longitude": activity["longitude"],
        }
        for activity in activities_json
        if activity.get("latitude") is not None
        and activity.get("longitude") is not None
        and activity["activity_id"] in allowed_ids  # Filter by ID
    ]
)

# Process accommodations
valid_locations.extend(
    [
        {
            "activity_id": accommodation[
                "accommodation_id"
            ],  # Use 'id' from accommodations
            "activity_name": accommodation["accommodation_name"],
            "latitude": accommodation[
                "latitude"
            ],  # Assuming accommodations have latitude
            "longitude": accommodation[
                "longitude"
            ],  # Assuming accommodations have longitude
        }
        for accommodation in accommodations_json
        if accommodation.get("latitude") is not None
        and accommodation.get("longitude") is not None
        and accommodation["accommodation_id"] in allowed_ids  # Filter by ID
    ]
)

# Sample 13 locations from the valid locations
sampled_locations = random.sample(valid_locations, k=min(13, len(valid_locations)))

# Prepare Mapbox API details
access_token = os.getenv("MAPBOX_API_KEY")
url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving"

# Initialize DataFrame to hold all durations
all_durations_df = pd.DataFrame(index=[loc["activity_id"] for loc in sampled_locations])

for i in range(len(sampled_locations)):
    for j in range(i + 1, len(sampled_locations)):
        # Prepare coordinates for the Mapbox Matrix API
        coordinates = ";".join(
            f"{loc['longitude']},{loc['latitude']}" for loc in sampled_locations
        )

        # Prepare the request URL
        request_url = f"{url}/{coordinates}?access_token={access_token}"

        # Make the API request
        response = requests.get(request_url)
        data = response.json()

        # Check if the response is OK
        if data.get("code") == "Ok":
            # Extract durations
            durations = data["durations"]

            # Update DataFrame with the new durations in hours multiplied by 4, rounded up
            for x in range(len(sampled_locations)):
                for y in range(len(sampled_locations)):
                    if durations[x][y] is not None:  # Check for valid duration
                        # Convert duration from seconds to hours, multiply by 4, and round up
                        duration_in_hours = math.ceil((durations[x][y] / 3600) * 4)
                        all_durations_df.at[
                            sampled_locations[x]["activity_id"],
                            sampled_locations[y]["activity_id"],
                        ] = duration_in_hours
                    else:
                        all_durations_df.at[
                            sampled_locations[x]["activity_id"],
                            sampled_locations[y]["activity_id"],
                        ] = None  # Handle null durations
        else:
            print(f"Error: {data.get('message', 'Unknown error occurred.')}")

# Print the consolidated durations DataFrame at the end
if not all_durations_df.empty:
    print("\nConsolidated Travel Time Matrix (in hours multiplied by 4, rounded up):")
    print(all_durations_df)

# Insert the results into MariaDB
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

try:
    connection = pymysql.connect(**db_config)

    # Create table if it doesn't exist
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS durations (
            source_id VARCHAR(255),
            destination_id VARCHAR(255),
            duration INT,
            PRIMARY KEY (source_id, destination_id)
        )"""
        )

        # Insert data into the table
        for i in range(len(sampled_locations)):
            for j in range(len(sampled_locations)):
                if i != j:  # Avoid inserting a location's duration to itself
                    source = sampled_locations[i]
                    destination = sampled_locations[j]
                    duration = all_durations_df.at[
                        source["activity_id"], destination["activity_id"]
                    ]

                    # Insert statement
                    insert_query = """
                    INSERT INTO durations (source_id, 
                                                  destination_id,
                                                  duration)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(
                        insert_query,
                        (
                            source["activity_id"],
                            destination["activity_id"],
                            duration,
                        ),
                    )
        connection.commit()  # Commit all inserts
        print("Data inserted successfully.")
except (pymysql.OperationalError, pymysql.ProgrammingError) as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    connection.close()  # Ensure the connection is closed
