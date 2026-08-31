from knowledge_loader import load_document, extract_toc, add_pdf_page_numbers, add_section_page_ranges


pages = load_document(
    "knowledge/leph1ps.pdf"
)

toc = extract_toc(pages)

toc = add_pdf_page_numbers(
    pages,
    toc
)

toc = add_section_page_ranges(
    toc,
    len(pages)
)

for entry in toc[:20]:

    print(
        f"{entry['section_number']} "
        f"{entry['section_title']}\n"
        f"  Book page: {entry['book_page']}\n"
        f"  PDF pages: "
        f"{entry['pdf_page_start']}-"
        f"{entry['pdf_page_end']}\n"
    )