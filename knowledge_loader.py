from pathlib import Path
from pypdf import PdfReader


def load_document(filename):

    path = Path(filename)

    if path.suffix.lower() == ".txt":

        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    if path.suffix.lower() == ".pdf":

        reader = PdfReader(str(path))

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text()

            if text:
                pages.append({
                    "page": page_number,
                    "text": text
                })

        return pages    

    raise ValueError(
        f"Unsupported file type: {path.suffix}"
    )

import re


def extract_toc(pages):

    toc_entries = []

    in_toc = False
    current_chapter_number = None
    current_chapter_title = None

    pending_section_number = None
    pending_section_title = None

    chapter_numbers = {
        "ONE": 1,
        "TWO": 2,
        "THREE": 3,
        "FOUR": 4,
        "FIVE": 5,
        "SIX": 6,
        "SEVEN": 7,
        "EIGHT": 8,
        "NINE": 9,
        "TEN": 10,
        "ELEVEN": 11,
        "TWELVE": 12
    }

    for page in pages:

        lines = [
            line.strip()
            for line in page["text"].splitlines()
            if line.strip()
        ]

        for line in lines:

            # Start of TOC
            if line.upper() == "CONTENTS":
                in_toc = True
                continue

            if not in_toc:
                continue

            # End of TOC
            if line.upper() == "ANSWERS":
                in_toc = False
                break

            # Detect chapter heading
            chapter_match = re.match(
                r"^CHAPTER\s+([A-Z]+)$",
                line,
                re.IGNORECASE
            )

            if chapter_match:

                word = chapter_match.group(1).upper()

                if word in chapter_numbers:

                    current_chapter_number = chapter_numbers[word]

                    # The chapter title is on the next line.
                    current_chapter_title = None

                continue

            # If we have just encountered a chapter heading,
            # the next line is the chapter title.
            if (
                current_chapter_number is not None
                and current_chapter_title is None
                and not re.match(r"^\d+\.\d+", line)
            ):

                current_chapter_title = line
                continue

            # Section with page number on the same line.
            match = re.match(
                r"^(\d+\.\d+)\s+(.+?)\s+(\d+)$",
                line
            )

            if match:

                section_number = match.group(1)
                section_title = match.group(2).strip()
                book_page = int(match.group(3))

                toc_entries.append({
                    "chapter_number": current_chapter_number,
                    "chapter_title": current_chapter_title,
                    "section_number": section_number,
                    "section_title": section_title,
                    "book_page": book_page
                })

                pending_section_number = None
                pending_section_title = None

                continue

            # Section title may wrap across two lines.
            # Example:
            #
            # 7.3 Representation of AC Current and Voltage by
            # Rotating Vectors — Phasors 181
            #
            partial_match = re.match(
                r"^(\d+\.\d+)\s+(.+)$",
                line
            )

            if partial_match:

                pending_section_number = partial_match.group(1)
                pending_section_title = partial_match.group(2).strip()

                continue

            # Complete a wrapped section title.
            if pending_section_number is not None:

                match = re.match(
                    r"^(.+?)\s+(\d+)$",
                    line
                )

                if match:

                    pending_section_title += " " + match.group(1).strip()

                    book_page = int(match.group(2))

                    toc_entries.append({
                        "chapter_number": current_chapter_number,
                        "chapter_title": current_chapter_title,
                        "section_number": pending_section_number,
                        "section_title": pending_section_title,
                        "book_page": book_page
                    })

                    pending_section_number = None
                    pending_section_title = None

    return toc_entries


def chunk_text(text):

    paragraphs = text.split("\n\n")

    chunks = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if paragraph:
            chunks.append(paragraph)

    return chunks

def add_pdf_page_numbers(pages, toc):

    if not toc:
        return toc

    first_entry = toc[0]

    target_number = first_entry["section_number"]

    target_title = first_entry["section_title"].upper()

    pdf_page = None

    for page in pages:

        text = page["text"].upper()

        if (
            target_number in text
            and target_title in text
        ):
            pdf_page = page["page"]
            break

    if pdf_page is None:
        raise ValueError(
            "Could not locate the first TOC section in the PDF."
        )

    offset = pdf_page - first_entry["book_page"]

    for entry in toc:

        entry["pdf_page_start"] = (
            entry["book_page"] + offset
        )

    return toc

def add_section_page_ranges(toc, total_pages):

    for i, entry in enumerate(toc):

        entry["pdf_page_start"] = entry["pdf_page_start"]

        if i + 1 < len(toc):

            entry["pdf_page_end"] = (
                toc[i + 1]["pdf_page_start"] - 1
            )

        else:

            entry["pdf_page_end"] = total_pages

    return toc