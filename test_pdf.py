from knowledge_loader import load_document


pages = load_document(
    "knowledge/leph1ps.pdf"
)

# print("Number of pages:", len(pages))

# print("\nFirst page:")
# print(pages[0]["text"])

# print("\nPage number:", pages[0]["page"])

# for page in pages[:5]:
#     print(f"\n===== PAGE {page['page']} =====")
#     print(page["text"])


for page in pages:

    lines = [
        line.strip()
        for line in page["text"].splitlines()
        if line.strip()
    ]

    if "CONTENTS" in lines:

        print(f"\n===== TOC PAGE {page['page']} =====")
        print(page["text"])