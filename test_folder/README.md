Technical Test — OCR + Information Extraction + CI/CD (Aircraft Maintenance)


**Goal:** Build a small pipeline that:
1) runs character recognition (ocr or any other methods you would like to approach) on scanned images (PNG/JPG),
2) extracts required fields into structured JSON,
3) outputs `results.json`,
4) passes lint + tests in CI (GitHub Actions).

This is a mini real-world task: turning scanned maintenance paperwork into structured data.

---

## Input data
All input images are in `_render/`.

**Only these files are graded** (see `manifest.json`):
- 01_TaskCard_TC-62-10-012-1.png
- 02_InspectionReport_IR-2201-1.png
- 03_NonRoutine_NR-7715-1.png
- 04_MaterialIssue_MIN-5530-1.png

Ignore any other images.

---

## Required output
Create `results.json` in the project root.

It must be a JSON list with **exactly 4 objects** (one per graded image):

```json
[
  {
    "doc_id": "TC-62-10-012",
    "doc_type": "task_card",
    "fields": { "task_card_no": "...", "...": "..." },
    "field_confidence": { "task_card_no": 0.95, "...": 0.80 },
    "extraction_notes": "Short note about OCR noise / assumptions."
  }
]

### Rules

- You MUST run OCR from the images. (No pre-extracted text is provided.)
- `doc_type` must be one of: `task_card`, `inspection_report`, `non_routine_defect`, `material_issue_note`
- `fields` must contain ALL required fields for that `doc_type` (below).
- `field_confidence` must contain the same keys as `fields`, each value in `[0,1]`.
- Normalize:
    - Dates: `YYYY-MM-DD`
    - Decimals: use dot (e.g., `1.6`, `2.3`)

## Required fields per doc_type

### task_card

- task_card_no
- work_order
- aircraft_type
- registration
- serial_no
- ata_chapter
- location
- date
- interval
- applicability

### inspection_report

- report_id
- related_work_order
- aircraft
- registration
- date
- inspector
- component
- measurement_value_mm
- limit_mm
- applicability

### non_routine_defect

- defect_id
- date
- task_card
- related_work_order
- aircraft
- registration
- serial_no
- severity
- crack_length_mm
- immediate_action

### material_issue_note

- issue_note
- date
- work_order
- location
- supplier
- destination
- part_number
- quantity
- batch_lot
- carrier

---

## What to implement

Implement:

- `src/ocr.py` (information extraction from image -> text)
- `src/extract.py` (extract fields from OCR text)

---

## How to run locally

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

### Install Tesseract

- Ubuntu/Debian: `sudo apt-get install -y tesseract-ocr`
- macOS (brew): `brew install tesseract`

### Run

```bash
make lint
make test
make run

```

This produces `results.json`.

---

## CI/CD task (small)

Fill `CI_NOTES.md` with 10–20 lines:

- what you would add in CI for OCR/ML pipelines (data checks, regression tests, quality gates)
- how you would deploy (CLI batch job, Docker, API, scheduled run)

---

## Submission

Submit either:

- a zipped folder
or
- Github repo

Include:

- your code
- `results.json`
- `CI_NOTES.md`

```

---

## 3) `CI_NOTES.md`
```md
# CI/CD Notes (10–20 lines)

Write briefly:
- What checks would you add in CI for character recognition (ocr or you may consider any other approach you would like too)  + extraction pipelines?
- How would you do data validation and regression tests (golden set)?
- How would you monitor extraction drift over time?
- How would you deploy (CLI batch job / Docker / API / scheduler)?

```
