import sys
import json
from sentence_transformers import SentenceTransformer

# example usage: cat ../f1db_json/circuits.json | python3 get_embeddings.py > ../f1db_json/semantic/circuits_semantic.json

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    # The model.encode() method already returns a list of floats
    return model.encode(text, convert_to_tensor=False).tolist()

if __name__ == "__main__":
    # Read JSON from STDIN
    data = json.load(sys.stdin)

    # Update each document in the JSON data
    for document in data:
        # Extract fields if they exist, otherwise default to empty strings
        circuitRef = document.get("circuitRef", "")
        name = document.get("name", "")
        location = document.get("location", "")
        country = document.get("country", "")
        circuit_bio = document.get("circuit_bio", "")

        combined_text = circuitRef + " " + name + " " + location + " " + country + " " + circuit_bio
        document["vector"] = get_embedding(combined_text)

    # Output updated JSON to STDOUT
    json.dump(data, sys.stdout, indent=4, ensure_ascii=False)
