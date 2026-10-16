"""Load documents and locate textbook sections for Project Cardinal.

The table of contents (TOC) is the source of truth for section names and
printed page numbers. PDF heading detection is used to locate those sections
in the supplied PDF; it is not intended to infer the TOC from body text.
"""

import re
from pathlib import Path

from pypdf import PdfReader


CHAPTER_NUMBERS = {
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
    "TWELVE": 12,
}


def load_document(filename):
    """Load a TXT file as text or a PDF as a list of page dictionaries.

    PDF page numbers are physical, 1-based PDF page numbers. Empty PDF pages
    are omitted, but each returned page retains its original PDF page number.
    """
    path = Path(filename)

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page": page_number, "text": text})

        return pages

    raise ValueError(f"Unsupported file type: {path.suffix}")


def normalize_text(text):
    """Normalize text for matching despite spaces and punctuation in PDFs."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def extract_toc(pages):
    """Extract chapter and numbered-section entries from pages containing a TOC.

    Expected section entries include a printed page number, either on the same
    line as the title or on the following line when the title wraps.
    """
    toc_entries = []
    in_toc = False
    current_chapter_number = None
    current_chapter_title = None
    pending_section_number = None
    pending_section_title = None

    for page in pages:
        lines = [
            line.strip()
            for line in page["text"].splitlines()
            if line.strip()
        ]

        for line in lines:
            upper_line = line.upper()

            if upper_line == "CONTENTS":
                in_toc = True
                pending_section_number = None
                pending_section_title = None
                continue

            if not in_toc:
                continue

            if upper_line == "ANSWERS":
                in_toc = False
                pending_section_number = None
                pending_section_title = None
                break

            chapter_match = re.match(
                r"^CHAPTER\s+([A-Z]+)$", line, re.IGNORECASE
            )
            if chapter_match:
                word = chapter_match.group(1).upper()
                current_chapter_number = CHAPTER_NUMBERS.get(word)
                current_chapter_title = None
                pending_section_number = None
                pending_section_title = None
                continue

            # In the TOC, a chapter title normally follows "CHAPTER ONE".
            if (
                current_chapter_number is not None
                and current_chapter_title is None
                and not re.match(r"^\d+\.\d+", line)
            ):
                current_chapter_title = line
                continue

            # Section number, title, and printed page on one line.
            match = re.match(r"^(\d+\.\d+)\s+(.+?)\s+(\d+)\s*$", line)
            if match:
                toc_entries.append({
                    "chapter_number": current_chapter_number,
                    "chapter_title": current_chapter_title,
                    "section_number": match.group(1),
                    "section_title": match.group(2).strip(),
                    "book_page": int(match.group(3)),
                })
                pending_section_number = None
                pending_section_title = None
                continue

            # A section title may start on one line and end with its page
            # number on the next line.
            partial_match = re.match(r"^(\d+\.\d+)\s+(.+?)\s*$", line)
            if partial_match:
                pending_section_number = partial_match.group(1)
                pending_section_title = partial_match.group(2).strip()
                continue

            if pending_section_number is not None:
                wrapped_match = re.match(r"^(.+?)\s+(\d+)\s*$", line)
                if wrapped_match:
                    title_continuation = wrapped_match.group(1).strip()
                    pending_section_title = (
                        f"{pending_section_title} {title_continuation}"
                    ).strip()
                    toc_entries.append({
                        "chapter_number": current_chapter_number,
                        "chapter_title": current_chapter_title,
                        "section_number": pending_section_number,
                        "section_title": pending_section_title,
                        "book_page": int(wrapped_match.group(2)),
                    })
                    pending_section_number = None
                    pending_section_title = None
                else:
                    # Preserve a title that wraps across more than two lines.
                    pending_section_title = (
                        f"{pending_section_title} {line}"
                    ).strip()

    return toc_entries


def chunk_text(text):
    """Split plain text into non-empty paragraph chunks."""
    return [part.strip() for part in text.split("\n\n") if part.strip()]




def _page_contains_heading(page_text, section_number, section_title):
    """Check for a top-level heading, excluding subsections and exercises."""

    number_pattern = re.compile(
        r"^\s*" + re.escape(section_number) + r"(?![\d.])(?:\s+|$)(.*)$",
        re.IGNORECASE,
    )
    title_normalized = normalize_text(section_title)
    lines = page_text.splitlines()

    for index, line in enumerate(lines):
        match = number_pattern.match(line)

        if not match:
            continue

        # The title must begin immediately after the section number.
        # Allow the title to continue over the next two lines.
        heading_text = " ".join(
            [match.group(1)] + lines[index + 1:index + 3]
        )
        normalized_heading = normalize_text(heading_text)

        if normalized_heading.startswith(title_normalized):
            return True

    return False


def add_pdf_page_numbers(pages, toc):
    """Add an estimated physical PDF start page to each TOC entry.

    This uses the first TOC section that can be found in the PDF to calculate
    a constant offset between printed book pages and physical PDF pages.
    This is appropriate only when the PDF is a continuous excerpt of the same
    book. For split, missing, or non-contiguous pages, use the candidate finder
    below to validate individual sections.
    """
    if not toc:
        return toc

    first_entry = toc[0]
    first_pdf_page = None

    for page in pages:
        if _page_contains_heading(
            page["text"],
            first_entry["section_number"],
            first_entry["section_title"],
        ):
            first_pdf_page = page["page"]
            break

    if first_pdf_page is None:
        raise ValueError(
            "Could not locate the first TOC section in the PDF. "
            "Check that the TOC and PDF refer to the same book/version."
        )

    offset = first_pdf_page - first_entry["book_page"]

    for entry in toc:
        entry["pdf_page_start"] = entry["book_page"] + offset

    return toc


def add_section_page_ranges(toc, total_pages):
    """Add rough section end pages based on the next section's start page.

    These ranges are estimates. Multiple sections can start on one page, so
    they should not be used as the sole method for extracting section bodies.
    """
    for index, entry in enumerate(toc):
        if index + 1 < len(toc):
            entry["pdf_page_end"] = toc[index + 1]["pdf_page_start"] - 1
        else:
            entry["pdf_page_end"] = total_pages

    return toc



def find_section_heading_candidates(
    pages,
    toc,
    pages_after_expected=3,
):
    """Find likely PDF pages for TOC sections.

    If an entry has no expected_pdf_page, search the entire PDF.
    Otherwise, search the expected page and following pages.
    """
    candidates = []

    for entry in toc:
        expected_page = entry.get("expected_pdf_page")

        section_number = entry["section_number"]
        section_title = entry["section_title"]

        matches = []

        for page in pages:
            page_number = page["page"]

            # Restrict the search only when an expected page is supplied.
            if expected_page is not None:
                if not (
                    expected_page
                    <= page_number
                    <= expected_page + pages_after_expected
                ):
                    continue

            if _page_contains_heading(
                page["text"],
                section_number,
                section_title,
            ):
                matches.append(page_number)

        candidates.append({
            "section_number": section_number,
            "section_title": section_title,
            "expected_pdf_page": expected_page,
            "candidate_pdf_pages": matches,
        })

    return candidates



def inspect_numbered_headings(pages):
    """Print likely uppercase, top-level numbered headings for diagnostics.

    The TOC should still determine which headings matter. This function is
    only a quick visual diagnostic and may miss headings affected by extraction
    artefacts or report false positives.
    """
    pattern = re.compile(
        r"^\s*(\d+\.\d+)\s{2,}([A-Z][A-Z\s\-–—,'()]+)\s*$"
    )

    for page in pages:
        for line_number, line in enumerate(page["text"].splitlines(), start=1):
            match = pattern.match(line)
            if not match:
                continue

            section_number = match.group(1)
            title = match.group(2).strip()

            if any(char.isdigit() for char in title):
                continue

            print(
                f"PDF page {page['page']}, line {line_number}: "
                f"{section_number} | {title}"
            )

def _find_heading_line_index(page_text, section_number, section_title):
    """Return the line index of a matching top-level section heading."""
    number_pattern = re.compile(
        r"^\s*" + re.escape(section_number) + r"(?![\d.])(?:\s+|$)(.*)$",
        re.IGNORECASE,
    )
    title_normalized = normalize_text(section_title)
    lines = page_text.splitlines()

    for index, line in enumerate(lines):
        match = number_pattern.match(line)

        if not match:
            continue

        heading_text = " ".join(
            [match.group(1)] + lines[index + 1:index + 3]
        )

        if normalize_text(heading_text).startswith(title_normalized):
            return index

    return None


def extract_sections(pages, toc):
    """Extract section text using TOC entries and detected headings.

    Returns a list of dictionaries containing section metadata and text.
    Sections that cannot be located are skipped.
    """
    locations = []

    for entry in toc:
        for page_index, page in enumerate(pages):
            line_index = _find_heading_line_index(
                page["text"],
                entry["section_number"],
                entry["section_title"],
            )

            if line_index is not None:
                locations.append({
                    **entry,
                    "pdf_page_start": page["page"],
                    "_page_index": page_index,
                    "_line_index": line_index,
                })
                break

    # Sort by physical PDF page and then by line position.
    locations.sort(
        key=lambda item: (item["_page_index"], item["_line_index"])
    )

    sections = []

    for index, location in enumerate(locations):
        start_page_index = location["_page_index"]
        start_line_index = location["_line_index"]

        if index + 1 < len(locations):
            next_location = locations[index + 1]
            end_page_index = next_location["_page_index"]
            end_line_index = next_location["_line_index"]

        else:
            # Default to the end of the PDF.
            end_page_index = len(pages) - 1
            end_line_index = len(
                pages[end_page_index]["text"].splitlines()
            )

            # For the final section of Chapter 1, stop before the exercises.
            if location["section_number"] == "1.14":
                for page_index, page in enumerate(pages):
                    lines = page["text"].splitlines()

                    for line_index, line in enumerate(lines):
                        if line.strip().startswith(
                            "1.14 Consider a uniform electric field"
                        ):
                            end_page_index = page_index
                            end_line_index = line_index
                            break
                    else:
                        continue

                    break


        text_parts = []

        for page_index in range(start_page_index, end_page_index + 1):
            lines = pages[page_index]["text"].splitlines()

            if page_index == start_page_index:
                lines = lines[start_line_index:]

            if page_index == end_page_index:
                lines = lines[:end_line_index]

            text_parts.append("\n".join(lines))

        sections.append({
            "section_number": location["section_number"],
            "section_title": location["section_title"],
            "book_page": location.get("book_page"),
            "pdf_page_start": location["pdf_page_start"],
            "text": "\n".join(text_parts).strip(),
        })

    return sections
