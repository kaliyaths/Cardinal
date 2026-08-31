import ollama

text = "Integration is the process of finding an integral."

response = ollama.embed(
    model="nomic-embed-text",
    input=text
)

embedding = response["embeddings"][0]

print("Number of values:", len(embedding))
print("First 10 values:", embedding[:10])