In CI, I would first run basic quality checks like linting and unit tests, followed by a small end-to-end smoke test that actually runs OCR on a few sample images and checks that a valid `results.json` is produced. This helps catch issues where OCR binaries or image paths are misconfigured.

For OCR and extraction pipelines, I would add simple data sanity checks: verify that input images exist, are readable, and are not empty or corrupted. I would also enforce schema checks on the output (required fields present per document type, correct date and decimal formats, confidence values within [0,1]).

For regression testing, I would maintain a small “golden dataset” of scanned documents with expected structured outputs. CI would compare current results against this reference set, allowing small numeric tolerances but failing if key fields or document IDs change unexpectedly.

To monitor extraction drift over time, I would track metrics such as field coverage, average confidence scores, and OCR text length per document type. Sudden drops or shifts would trigger alerts for manual review.

For deployment, I would start with a CLI-based batch job for offline processing, package it in a Docker image with Tesseract installed for consistency, and optionally expose it as an API for on-demand use. Scheduled runs (cron or CI scheduler) could be used to process new documents automatically.
