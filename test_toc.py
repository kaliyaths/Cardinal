"""Test TOC extraction, section-heading detection, and section extraction.

Run from the Project Cardinal root directory:
    python test_toc.py

This test uses:
- knowledge/leph1ps.pdf for the table of contents
- knowledge/leph101.pdf for Chapter 1 section text
"""

from knowledge_loader import load_document, extract_toc, extract_sections


# 1. Extract the table of contents from the TOC/textbook PDF.
toc_pages = load_document("knowledge/leph1ps.pdf")
toc = extract_toc(toc_pages)

print(f"TOC entries extracted: {len(toc)}")

# 2. Load the PDF excerpt containing Chapter 1.
chapter_pages = load_document("knowledge/leph101.pdf")
print(f"Chapter PDF pages loaded: {len(chapter_pages)}")

# 3. Keep only Chapter 1 sections from the TOC.
chapter_1_toc = [
    entry for entry in toc
    if entry["section_number"].startswith("1.")
]

# 4. Locate and extract the Chapter 1 sections.
sections = extract_sections(chapter_pages, chapter_1_toc)

print(f"\nSections extracted: {len(sections)}")
print("\n--- Section summary and boundary sanity checks ---")

for i, section in enumerate(sections):
    next_section = (
        sections[i + 1]["section_number"]
        if i + 1 < len(sections)
        else None
    )

    starts_correctly = section["text"].lstrip().startswith(
        section["section_number"]
    )

    next_heading_present = False
    if next_section:
        next_heading_present = (
            f"{next_section} " in section["text"]
        )

    print(
        f"{section['section_number']} | "
        f"{section['section_title']} | "
        f"PDF page {section['pdf_page_start']} | "
        f"{len(section['text'])} characters | "
        f"starts correctly: {starts_correctly} | "
        f"next section: {next_section} | "
        f"next heading text present: {next_heading_present}"
    )

# 5. Inspect Section 1.5 (Coulomb's Law).
section_15 = next(
    (s for s in sections if s["section_number"] == "1.5"),
    None,
)

if section_15:
    print("\n--- Beginning of Section 1.5 ---")
    print(section_15["text"][:1000])

    print("\n--- End of Section 1.5 ---")
    print(section_15["text"][-500:])
else:
    print("\nWARNING: Section 1.5 was not extracted.")

# 6. Check that Section 1.14 stops before Exercise 1.14.
section_114 = next(
    (s for s in sections if s["section_number"] == "1.14"),
    None,
)

if section_114:
    exercise_marker = "1.14 Consider a uniform electric field"
    contains_exercise = exercise_marker in section_114["text"]

    print("\n--- Section 1.14 boundary check ---")
    print("--- Last 1000 characters of Section 1.14 ---")
    print(section_114["text"][-1000:])
    print(f"Contains Exercise 1.14: {contains_exercise}")

    if contains_exercise:
        print("WARNING: Section 1.14 includes Exercise 1.14.")
else:
    print("\nWARNING: Section 1.14 was not extracted.")

# 7. Report whether the basic checks passed.
expected_sections = 14
section_numbers = [s["section_number"] for s in sections]
all_sections_found = len(sections) == expected_sections
all_start_correct = all(
    s["text"].lstrip().startswith(s["section_number"])
    for s in sections
)
exercise_excluded = (
    section_114 is not None
    and "1.14 Consider a uniform electric field" not in section_114["text"]
)

print("\n--- Overall checks ---")
print(f"Expected {expected_sections} sections: {all_sections_found}")
print(f"All section texts start with their section number: {all_start_correct}")
print(f"Exercise 1.14 excluded from Section 1.14: {exercise_excluded}")

if not all_sections_found or not all_start_correct or not exercise_excluded:
    print("\nOne or more checks failed. Review the diagnostics above.")
else:
    print("\nBasic extraction checks passed.")
