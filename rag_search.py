import ollama
import math
import json

from knowledge_loader import load_document, chunk_text



def get_embedding(text):

    response = ollama.embed(
        model="nomic-embed-text",
        input=text
    )

    return response["embeddings"][0]

def load_index(index_filename):

    with open(
        index_filename,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def cosine_similarity(vector_a, vector_b):

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (magnitude_a * magnitude_b)


def search_chunks(question, index):

    question_embedding = get_embedding(question)

    results = []

    for item in index:

        similarity = cosine_similarity(
            question_embedding,
            item["embedding"]
        )

        results.append(
            (similarity, item["text"])
        )

    results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return results


def generate_rag_answer(question, results):

    relevant_chunks = results[:2]

    context = "\n\n".join(
        chunk
        for score, chunk in relevant_chunks
    )

    prompt = f"""
You are a helpful home tutor.

Use the following knowledge to answer the student's question.

KNOWLEDGE:
{context}

STUDENT QUESTION:
{question}

Answer using the supplied knowledge.
If the knowledge does not contain enough information, say so.

Do not invent facts that are not supported by the knowledge.
"""

    response = ollama.chat(
        model="phi4-mini:latest",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


index = load_index(
    "mathematics_index.json"
)

question = "How is integration related to differentiation?"

results = search_chunks(
    question,
    index
)

# print("\n--- Retrieved Knowledge ---")

# for score, chunk in results[:2]:

#     print("\nSimilarity:", score)
#     print(chunk)

answer = generate_rag_answer(
    question,
    results
)

# print("\n--- Phi-4 Answer ---")
# print(answer)