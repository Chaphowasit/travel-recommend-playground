import os
import weaviate
import json
from weaviate.classes.query import Rerank, MetadataQuery
from dotenv import load_dotenv
import os
import weaviate
import weaviate.classes as wvc
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, render_template, request
from weaviate.classes.init import Auth
from weaviate.classes.query import Rerank, MetadataQuery


load_dotenv()
headers = {
    "X-OpenAI-Api-Key": os.getenv("OPENAI_APIKEY"),
    "X-Cohere-Api-Key": os.getenv("COHERE_KEY"),
}

# Connect to Weaviate
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers=headers,
)


# Define the K value for hit@k
K = 3


def calculate_hit_k(results, correct_label, k=K):
    """
    Function to calculate hit@k score.
    :param results: List of results returned by the search.
    :param correct_label: The correct label (place) for the query (e.g., accommodation or activity).
    :param k: The number of top results to check.
    :return: 1 if correct label is within the top k results, 0 otherwise.
    """
    top_k_results = results[:k]
    for result in top_k_results:
        if result.get("name") == correct_label:
            return 1
    return 0


def fetch_search_results(reviews, category, label_key, rerank=False):
    """
    Function to fetch search results from Weaviate.
    :param query: The search query.
    :param category: Either 'Activity_Embedded' or 'Accommodation_Embedded'.
    :param rerank: Whether to apply Rerank or not.
    :return: List of results.
    """
    client_collection = client.collections.get(category)

    if rerank:
        # Perform search with rerank
        search_response = client_collection.query.hybrid(
            query=reviews,
            limit=K,
            rerank=Rerank(prop=f"{label_key}", query=reviews),
            return_metadata=MetadataQuery(score=True),
        )
    else:
        # Perform normal search (without rerank)
        search_response = client_collection.query.hybrid(query=reviews, limit=K)

    # Extract the results
    return [
        {"name": res.properties.get(f"{label_key}", "Unknown")}
        for res in search_response.objects
    ]


def evaluate_hit_k(data, category, label_key):
    """
    Function to evaluate hit@k for a given category (either activity or accommodation).
    :param data: List of dictionaries containing {query: reviews}.
    :param category: Either 'Activity_Embedded' or 'Accommodation_Embedded'.
    :param label_key: The key for extracting the correct label ('accommodation_name' or 'activity_name').
    :return: hit@k score before and after rerank.
    """
    total = len(data)
    hit_k_before = 0
    hit_k_after = 0

    for entry in data:
        for (
            query,
            reviews,
        ) in entry.items():  # Loop through key-value pairs in the dictionary
            correct_label = query  # The correct label is the key (name)
            if query and correct_label:
                # Fetch results without Rerank
                results_before_rerank = fetch_search_results(
                    reviews, category, label_key, rerank=False
                )
                # Fetch results with Rerank
                results_after_rerank = fetch_search_results(
                    reviews, category, label_key, rerank=True
                )

                # Calculate hit@k before rerank
                hit_k_before += calculate_hit_k(
                    results_before_rerank, correct_label, k=K
                )
                # Calculate hit@k after rerank
                hit_k_after += calculate_hit_k(results_after_rerank, correct_label, k=K)

    hit_k_before_percentage = (hit_k_before / total) * 100
    hit_k_after_percentage = (hit_k_after / total) * 100

    return hit_k_before_percentage, hit_k_after_percentage


def load_data_from_json(folder_path, label_key):
    """
    Load data from JSON files in a given folder.
    :param folder_path: The path to the folder containing the JSON files.
    :param label_key: The key for extracting the label ('accommodation_name' or 'activity_name').
    :return: List of dictionaries with the format {label: reviews}.
    """
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                file_data = json.load(file)
                # Collect each entry's query (label) and reviews (ground truth)
                data.extend(
                    [
                        {entry.get(label_key): entry.get("reviews", [])}
                        for entry in file_data
                    ]
                )
    return data


if __name__ == "__main__":
    # Load accommodation data
    accommodation_data = load_data_from_json(
        "stay/extract_json_1review", "accommodation_name"
    )
    activity_data = load_data_from_json("do/extract_json_1review", "activity_name")

    # Evaluate hit@k for Accommodation
    accommodation_hit_k_before, accommodation_hit_k_after = evaluate_hit_k(
        accommodation_data,
        category="Accommodation_Embedded",
        label_key="accommodation_name",
    )
    print(f"Accommodation hit@{K} before rerank: {accommodation_hit_k_before}%")
    print(f"Accommodation hit@{K} after rerank: {accommodation_hit_k_after}%")

    # Evaluate hit@k for Activity
    activity_hit_k_before, activity_hit_k_after = evaluate_hit_k(
        activity_data, category="Activity_Embedded", label_key="activity_name"
    )
    print(f"Activity hit@{K} before rerank: {activity_hit_k_before}%")
    print(f"Activity hit@{K} after rerank: {activity_hit_k_after}%")
