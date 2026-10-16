# Project Cardinal — Current State

## Objective

Project Cardinal is a local, Python-based AI home tutor designed primarily for one student. It uses textbook material (currently NCERT Physics content) to ground explanations and follows a controlled Socratic approach: one teaching move at a time, normally 2–4 sentences and at most one question. The longer-term aim is an adaptive tutor with retrieval-augmented generation (RAG), student/topic progress tracking, and learning-session memory.

## Environment

- **OS:** Windows.
- **Active Git-aware project folder:** `C:\Project Cardinal-sync`.
- **Legacy/original folder:** `C:\Project Cardinal` is the earlier project location/source backup. Use the `Project Cardinal-sync` folder for current development, testing, commits, and GitHub sync.
- **Python version:** Python 3.14 was reported earlier. Reconfirm with `python --version` if the environment has changed.
- **Virtual environment:** A virtual environment is used/being recreated as needed. Exact folder name and activation command are not confirmed in this status update.
- **Model/runtime:** Ollama local runtime; chat model `qwen3.5:2b`; embedding model `nomic-embed-text`.
- **Dependencies:** Check `requirements.txt` in the active repository. Known dependencies include `ollama` and `pypdf`; verify other dependencies from the current file.

## Architecture

- `app.py` — Console application entry point; loads/creates the student profile, displays topic progress, runs the tutor interaction loop, and records session progress.
- `config.py` — Application configuration, including model and student settings. Verify actual variable names before changing them.
- `tutor/tutor.py` — Tutor conversation, retrieval calls, prompt construction, evidence classification, and progress/confidence methods.
- `student/student.py` — Student profile representation.
- `database/database.py` — SQLite persistence for student profiles and topic progress.
- `knowledge_loader.py` — Loads TXT/PDF documents, extracts the TOC, normalizes text, detects TOC-listed section headings, and extracts section text.
- `rag_search.py` — Embedding generation, loading the JSON embedding index, cosine similarity, and chunk search.
- `embedding_index.py` — Existing embedding/index-building workflow; inspect before integrating section-aware chunks.
- `prompts.py` — System and evidence-classification prompts.
- `knowledge/` — Source material, including `leph1ps.pdf`, `leph101.pdf`, and `mathematics.txt`.
- `mathematics_index.json` — Existing embedding index; do not overwrite/rebuild until the new chunking workflow has been tested.
- `test_toc.py` — TOC and section-extraction test.
- `test_chunking.py` — Planned test for section-aware chunking; create/run it in the next session.
- `docs/` — Development journal and reflection notes.

## Working Features

- Local Ollama chat has been installed and tested previously.
- PDF and TXT loading is implemented in `knowledge_loader.py`.
- TOC extraction currently returns 77 entries from `leph1ps.pdf`.
- Chapter 1 section headings are detected in `leph101.pdf`.
- The 14 Chapter 1 sections (1.1–1.14) are extracted using TOC entries and heading locations.
- Section extraction stops Section 1.14 before Exercise 1.14 using a targeted marker in the current implementation.
- The consolidated `test_toc.py` has been run successfully:
  - 14 sections extracted.
  - Each extracted section starts with its section number.
  - Exercise 1.14 is excluded from Section 1.14.

## Current Development

Latest work focused on textbook parsing and section extraction:
1. Extracted the TOC from `leph1ps.pdf`.
2. Used it as the source of truth for Chapter 1 section numbers, titles, and printed page numbers.
3. Searched `leph101.pdf` independently to locate physical PDF pages for the Chapter 1 headings.
4. Fixed false-positive heading matches by requiring a section-number boundary, so `1.7.1` is not treated as top-level section `1.7`.
5. Added `extract_sections()` to collect text from each section heading up to the next detected section heading.
6. Added a specific stop condition before `1.14 Consider a uniform electric field`, the beginning of Exercise 1.14 in this PDF.
7. The next proposed task is section-aware chunking; its implementation and test status must be confirmed.
8. The active repository location changed to `C:\Project Cardinal-sync`. All new edits, tests, status updates, and Git operations should be performed from that folder.

## Known Issues

- The Section 1.14 exercise-boundary rule is hard-coded to the current PDF text and must be generalized before processing arbitrary chapters or textbook versions.
- The final section in any PDF may run to the end of the file unless an explicit end boundary is identified.
- PDF text extraction can corrupt equations, symbols, spacing, and some headings; extracted text may not preserve mathematical notation perfectly.
- `pdf_page_start` currently records the section's starting page, not the exact page for every chunk.
- TOC extraction and page mapping must remain separate: `leph1ps.pdf` and `leph101.pdf` have different physical page numbering.
- Current section extraction checks are basic structural tests; they do not prove every section contains only its intended material.
- `chunk_sections()` was proposed but has not been confirmed as added to `knowledge_loader.py` or tested.
- `test_chunking.py` was proposed but has not been confirmed as created or run.
- Existing `rag_search.py` has a standalone test block that executes on import and references a stale model (`phi4-mini:latest`); guard the test with `if __name__ == "__main__":` and align model configuration before integrating.
- `rag_search.py` currently returns `(similarity, text)` tuples, so metadata-bearing chunks will require a deliberate compatibility decision.
- The constant-offset `add_pdf_page_numbers()` approach is not appropriate for searching one PDF using offsets calculated from another PDF.
- Confidence calculation and evidence classification are not the focus of this work and should not be retuned unless requested.

## Decisions

- Use `C:\Project Cardinal-sync` as the canonical working repository for development and GitHub sync.
- Treat `C:\Project Cardinal` as the legacy/original location; do not accidentally run tests or commits from it.
- Prioritize a useful working tutor for one student; avoid premature multi-user features and elaborate abstractions.
- Use NCERT source text and the TOC as the source of truth for section identities and titles.
- Locate headings in the actual chapter PDF rather than relying on a constant offset from a different PDF.
- Keep each extracted section associated with its section number and title.
- Develop incrementally: change one thing, run a focused test, inspect the output, then proceed.
- Do not rebuild or overwrite the current embedding index until section-aware chunking and retrieval have been tested.
- Preserve the working heading detector and current extraction workflow while extending it carefully.
- Keep confidence-score tuning parked unless explicitly requested.

## Next Steps

1. **Immediate:** In `C:\Project Cardinal-sync`, confirm `chunk_sections()` is added to `knowledge_loader.py`, then create and run `test_chunking.py` to inspect chunk counts, sizes, metadata, and text continuity.
2. Review chunk boundaries and handle long paragraphs/overlap without unintended text loss or excessive duplication.
3. Integrate section-aware chunks into `embedding_index.py`, generate embeddings with `nomic-embed-text`, and test retrieval against representative Physics questions.
4. Update `rag_search.py` to consume the new chunk format while preserving compatibility with `tutor/tutor.py`.
5. Later: generalize exercise detection, improve page-level provenance, and test additional chapters/PDF versions.
6. At the end of each development session, update this file, commit the relevant code and status changes, and sync the active folder with GitHub.

## Verification

**Tests run and results**
- `test_toc.py`: passed the basic checks:
  - `Expected 14 sections: True`
  - `All section texts start with their section number: True`
  - `Exercise 1.14 excluded from Section 1.14: True`
- Heading-candidate test: all 14 Chapter 1 headings were found on one expected physical PDF page each:
  - 1.1 → 1; 1.2 → 1; 1.3 → 3; 1.4 → 4; 1.5 → 6; 1.6 → 11; 1.7 → 14; 1.8 → 19; 1.9 → 21; 1.10 → 23; 1.11 → 27; 1.12 → 28; 1.13 → 29; 1.14 → 33.
- TOC extraction: 77 entries extracted from `leph1ps.pdf`.
- Chunking: not yet tested.
- RAG retrieval using the newly extracted section chunks: not yet tested.

## Resume Instructions

1. Open a terminal in `C:\Project Cardinal-sync` (not the legacy folder).
2. Check the active directory with `Get-Location`.
3. Open `knowledge_loader.py` and `test_toc.py`.
4. Confirm `extract_sections()` includes the targeted Section 1.14 exercise stop marker.
5. Confirm whether `chunk_sections()` has actually been added. If not, add and test it; do not assume the proposed code was applied.
6. Create `test_chunking.py`, then run:
   `python test_chunking.py`
7. Share the output showing chunk count, chunks per section, sample chunk metadata/text, and validation checks.
8. Do not modify `embedding_index.py`, `rag_search.py`, or `mathematics_index.json` until chunking results have been reviewed.
