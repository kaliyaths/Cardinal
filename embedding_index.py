import json

import ollama

from knowledge_loader import load_document, chunk_text


def get_embedding(text):

    response = ollama.embed(
        model="nomic-embed-text",
        input=text
    )

    return response["embeddings"][0]


def create_index(filename, index_filename):

    text = load_document(filename)

    chunks = chunk_text(text)

    index = []

    for chunk in chunks:

        embedding = get_embedding(chunk)

        index.append({
            "text": chunk,
            "embedding": embedding
        })

    with open(index_filename, "w", encoding="utf-8") as file:

        json.dump(
            index,
            file
        )

    print(f"Saved {len(index)} chunks.")


create_index(
    "knowledge/mathematics.txt",
    "mathematics_index.json"
)


# Test

with open(
    "mathematics_index.json",
    "r",
    encoding="utf-8"
) as file:

    index = json.load(file)

print("Loaded chunks:", len(index))

print("First chunk:")
print(index[0]["text"])

print("Embedding length:")
print(len(index[0]["embedding"]))