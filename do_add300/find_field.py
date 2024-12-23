import json

# Open and load the JSON file
with open(
    "do_add300/extract_json_version2_noDup_image/output.json", "r", encoding="utf-8"
) as file:
    json_data = json.load(file)

# Find activity IDs where "image_url" is missing
missing_image_activities = [
    obj["activity_id"] for obj in json_data if "nearby_accommodation3" not in obj
]

print("Activity IDs without image_url:", missing_image_activities)
