import json
import os
import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth
import weaviate.classes.config as wc

CATEGORIES = {
    # "RESTAURANT": ["foodAndDrink_Embedded", "foodAndDrink_Bridge"],
    "ACCOMMODATION": ["accommodation_Embedded", "accommodation_Bridge"],
    "ACTIVITY": ["activity_Embedded", "activity_Bridge"],
}


def connect_to_weaviate():
    """Connect to Weaviate Cloud and return the client object."""
    load_dotenv()
    headers = {
        "X-OpenAI-Api-Key": os.getenv("OPENAI_APIKEY")
    }  # Replace with your OpenAI API key
    weaviate_url = os.getenv("WEAVIATE_URL")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key),
        headers=headers,
    )
    print(os.getenv("OPENAI_APIKEY"))

    # client = weaviate.connect_to_weaviate_cloud(..., headers=headers) or
    # client = weaviate.connect_to_local(..., headers=headers)

    # client = weaviate.connect_to_local(
    #     host="127.0.0.1",  # Use a string to specify the host
    #     port=8082,
    #     grpc_port=50051,
    #     headers=headers,
    # )
    if client.is_ready():
        print("Connected to Weaviate Cloud successfully!")
    else:
        print("Failed to connect to Weaviate Cloud.")
        client = None
    return client


def create_collection(client, collection_name):
    client.collections.create(
        f"{collection_name}",
        # Define the vectorizer module
        vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(),
        # Define the generative module
        generative_config=wc.Configure.Generative.openai(),
        reranker_config=wc.Configure.Reranker.cohere(),
    )


# def insert_data(client, collection_name, object_data):
#     """Insert data into a specified collection."""
#     obj = client.collections.get(f"{collection_name}")
#     uuid = obj.data.insert(properties=object_data)


def list_collections(client):
    response = client.collections.list_all(simple=True)
    print(response.keys())
    return len(response.keys())


# def extract_data(json_data, collection_name):
#     if collection_name == "foodAndDrink_Embedded":
#         return {
#             "foodAndDrink_name": json_data.get("foodAndDrink_name"),
#             "about_and_tags": str(json_data.get("about_and_tags")),
#             "latitude": json_data.get("latitude"),
#             "longitude": json_data.get("longitude"),
#             "reviews": str(json_data.get("reviews")),
#         }
#     elif collection_name == "foodAndDrink_Bridge":
#         return {
#             "foodAndDrink_id": json_data.get("foodAndDrink_id"),
#             "foodAndDrink_name": json_data.get("foodAndDrink_name"),
#             "latitude": json_data.get("latitude"),
#             "longitude": json_data.get("longitude"),
#         }
#     elif collection_name == "accommodation_Embedded":
#         return {
#             "accommodation_name": json_data.get("accommodation_name"),
#             "about_and_tags": str(json_data.get("about_and_tags")),
#             "latitude": json_data.get("latitude"),
#             "longitude": json_data.get("longitude"),
#             "reviews": json_data.get("reviews"),
#         }
#     elif collection_name == "accommodation_Bridge":
#         return {
#             "accommodation_id": json_data.get("accommodation_id"),
#             "accommodation_name": json_data.get("accommodation_name"),
#             "latitude": json_data.get("latitude"),
#             "longitude": json_data.get("longitude"),
#         }
#     elif collection_name == "activity_Embedded":
#         return {
#             "activity_name": json_data.get("activity_name"),
#             "about_and_tags": str(json_data.get("about_and_tags")),
#             "latitude": json_data.get("latitude"),
#             "longitude": json_data.get("longitude"),
#             "reviews": json_data.get("reviews"),
#         }
#     elif collection_name == "activity_Bridge":
#         return {
#             "activity_id": json_data.get("activity_id"),
#             "activity_name": json_data.get("activity_name"),
#             "latitude": json_data.get("latitude"),
#             "longitude": json_data.get("longitude"),
#         }


# def process_json_files(client, json_directory):
#     json_files = [f for f in os.listdir(json_directory) if f.endswith(".json")]
#     relevant_categories = []
#     if "eat" in json_directory.lower():
#         relevant_categories = {
#             "RESTAURANT": ["foodAndDrink_Embedded", "foodAndDrink_Bridge"]
#         }
#     elif "stay" in json_directory.lower():
#         relevant_categories = {
#             "ACCOMMODATION": ["accommodation_Embedded", "accommodation_Bridge"]
#         }
#     elif "do" in json_directory.lower():
#         relevant_categories = {"ACTIVITY": ["activity_Embedded", "activity_Bridge"]}
#     for json_file in json_files:
#         input_file = os.path.join(json_directory, json_file)
#         with open(input_file, "r", encoding="utf-8") as file:
#             json_data = json.load(file)
#         if not json_data:
#             continue
#     for category, collections in relevant_categories.items():
#         for collection in collections:
#             for json_dict in json_data:
#                 data = extract_data(json_dict, collection)
#                 insert_data(client, collection, data)


def insert_data(client, collection_name, object_data_list):
    """Insert multiple data items into a specified collection."""
    obj = client.collections.get(f"{collection_name}")
    # Insert multiple objects at once using insert_many
    obj.data.insert_many(object_data_list)


def extract_data(json_data, collection_name):
    if collection_name == "accommodation_Embedded":
        return {
            "name": json_data.get("accommodation_name"),
            "about_and_tags": str(json_data.get("about_and_tags")),
            "latitude": json_data.get("latitude"),
            "longitude": json_data.get("longitude"),
            "reviews": json_data.get("reviews"),
        }
    elif collection_name == "accommodation_Bridge":
        return {
            "accommodation_id": json_data.get("accommodation_id"),
            "name": json_data.get("accommodation_name"),
            "latitude": json_data.get("latitude"),
            "longitude": json_data.get("longitude"),
        }
    elif collection_name == "activity_Embedded":
        return {
            "name": json_data.get("activity_name"),
            "about_and_tags": str(json_data.get("about_and_tags")),
            "latitude": json_data.get("latitude"),
            "longitude": json_data.get("longitude"),
            "reviews": json_data.get("reviews"),
        }
    elif collection_name == "activity_Bridge":
        return {
            "activity_id": json_data.get("activity_id"),
            "name": json_data.get("activity_name"),
            "latitude": json_data.get("latitude"),
            "longitude": json_data.get("longitude"),
        }


# def process_json_files(client, json_directory):
#     json_files = [f for f in os.listdir(json_directory) if f.endswith(".json")]
#     relevant_categories = []

#     if "eat" in json_directory.lower():
#         relevant_categories = {
#             "RESTAURANT": ["foodAndDrink_Embedded", "foodAndDrink_Bridge"]
#         }
#     elif "stay" in json_directory.lower():
#         relevant_categories = {
#             "ACCOMMODATION": ["accommodation_Embedded", "accommodation_Bridge"]
#         }
#     elif "do" in json_directory.lower():
#         relevant_categories = {"ACTIVITY": ["activity_Embedded", "activity_Bridge"]}

#     for json_file in json_files:
#         input_file = os.path.join(json_directory, json_file)
#         with open(input_file, "r", encoding="utf-8") as file:
#             json_data = json.load(file)

#         if not json_data:
#             continue

#         for category, collections in relevant_categories.items():
#             for collection in collections:
#                 data_list = []
#                 for json_dict in json_data:
#                     data = extract_data(json_dict, collection)
#                     data_list.append(data)

#                 # Insert multiple data points at once
#                 if data_list:
#                     insert_data(client, collection, data_list)


def process_json_files(
    client, json_directory, batch_size=100
):  # Add batch_size parameter
    json_files = [f for f in os.listdir(json_directory) if f.endswith(".json")]
    relevant_categories = []

    # if "eat" in json_directory.lower():
    #     relevant_categories = {
    #         "RESTAURANT": ["foodAndDrink_Embedded", "foodAndDrink_Bridge"]
    #     }
    if "stay" in json_directory.lower():
        relevant_categories = {
            "ACCOMMODATION": ["accommodation_Embedded", "accommodation_Bridge"]
        }
    elif "do" in json_directory.lower():
        relevant_categories = {"ACTIVITY": ["activity_Embedded", "activity_Bridge"]}

    for json_file in json_files:
        input_file = os.path.join(json_directory, json_file)
        with open(input_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        if not json_data:
            continue

        for category, collections in relevant_categories.items():
            for collection in collections:
                data_list = []
                for json_dict in json_data:
                    data = extract_data(json_dict, collection)
                    data_list.append(data)

                    # Process data in batches
                    if len(data_list) >= batch_size:
                        insert_data(client, collection, data_list)
                        data_list.clear()  # Clear the list after inserting

                # Insert remaining data after batch processing
                if data_list:
                    insert_data(client, collection, data_list)


def delete_collections(client):
    for category, collections in CATEGORIES.items():
        for collection in collections:
            client.collections.delete(f"{collection}")
            print(f"Collection '{collection}' deleted.")


def main():
    client = connect_to_weaviate()
    # if list_collections(client) > 0:
    #     delete_collections(client)
    # if client:
    #     for category, collections in CATEGORIES.items():
    #         for collection in collections:
    #             create_collection(client, collection)
    directories = [
        "stay/extract_json_1review",
        "do/extract_json_1review",
    ]
    for directory in directories:
        process_json_files(client, directory)
    list_collections(client)
    client.close()


if __name__ == "__main__":
    main()
