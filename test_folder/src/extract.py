from __future__ import annotations

import re
from typing import Any

REQUIRED_FIELDS: dict[str, list[str]] = {
    "task_card": [
        "task_card_no",
        "work_order",
        "aircraft_type",
        "registration",
        "serial_no",
        "ata_chapter",
        "location",
        "date",
        "interval",
        "applicability",
    ],
    "inspection_report": [
        "report_id",
        "related_work_order",
        "aircraft",
        "registration",
        "date",
        "inspector",
        "component",
        "measurement_value_mm",
        "limit_mm",
        "applicability",
    ],
    "non_routine_defect": [
        "defect_id",
        "date",
        "task_card",
        "related_work_order",
        "aircraft",
        "registration",
        "serial_no",
        "severity",
        "crack_length_mm",
        "immediate_action",
    ],
    "material_issue_note": [
        "issue_note",
        "date",
        "work_order",
        "location",
        "supplier",
        "destination",
        "part_number",
        "quantity",
        "batch_lot",
        "carrier",
    ],
}


def _clean(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\r\n?", "\n", text)
    return text.strip()


def _first_line(s: str) -> str:
    return s.split("\n", 1)[0].strip()


def normalize_decimal(s: str) -> str:
    s0 = s.replace(",", ".")
    m = re.search(r"[-+]?\d+(?:\.\d+)?", s0)
    return m.group(0) if m else s0


def normalize_date(s: str) -> str:
    s0 = re.sub(r"\s+", " ", s.strip())

    # YYYY-MM-DD
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", s0)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # DD.MM.YYYY / DD-MM-YYYY / DD/MM/YYYY
    m = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b", s0)
    if m:
        dd, mm, yyyy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{yyyy:04d}-{mm:02d}-{dd:02d}"

    # 16 Jan 2025
    months = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})\b", s0)
    if m:
        dd = int(m.group(1))
        mm = months.get(m.group(2).lower()[:3])
        yyyy = int(m.group(3))
        if mm:
            return f"{yyyy:04d}-{mm:02d}-{dd:02d}"

    return s0


def _score(found: bool, value: str) -> float:
    if not found or not value:
        return 0.0
    if len(value) <= 2:
        return 0.7
    return 0.9


def _detect_doc_type_and_id(text: str) -> tuple[str, str]:
    if m := re.search(r"\bTC-\d{2}-\d{2}-\d{3}\b", text, re.I):
        return "task_card", m.group(0).upper()
    if m := re.search(r"\bIR-\d{3,6}\b", text, re.I):
        return "inspection_report", m.group(0).upper()
    if m := re.search(r"\bNR-\d{3,6}\b", text, re.I):
        return "non_routine_defect", m.group(0).upper()
    if m := re.search(r"\bMIN-\d{3,6}\b", text, re.I):
        return "material_issue_note", m.group(0).upper()

    return "task_card", ""


def extract_fields(filename: str, ocr_text: str) -> dict[str, Any]:
    """
    Main extraction entrypoint.
    doc_id and doc_type are detected from OCR TEXT (not filename).
    """
    text = _clean(ocr_text)
    doc_type, doc_id = _detect_doc_type_and_id(text)

    fields: dict[str, str] = {}
    confidence: dict[str, float] = {}
    notes: list[str] = []

    def find(label: str, pattern: str) -> str | None:
        m = re.search(rf"{label}.*?({pattern})", text, re.I | re.S)
        return _first_line(m.group(1)) if m else None

    def put(key: str, value: str | None, normalize=None) -> None:
        if value is None:
            fields[key] = ""
            confidence[key] = 0.0
            notes.append(f"Missing {key}")
            return

        if normalize:
            value = normalize(value)

        fields[key] = value
        confidence[key] = _score(True, value)

    # ---------------- TASK CARD ----------------
    if doc_type == "task_card":
        put("task_card_no", doc_id)
        put("work_order", find("Work Order", r"[A-Z0-9\-]+"))
        put("aircraft_type", find("Aircraft", r".+"), _first_line)
        put("registration", find("Registration", r"[A-Z0-9\-]+"))
        put("serial_no", find("Serial", r"[A-Z0-9\-]+"))
        put("ata_chapter", find("ATA", r"\d{2}-\d{2}"))
        put("location", find("Location", r".+"), _first_line)
        put("date", find("Date", r".+"), normalize_date)
        put("interval", find("Interval", r".+"), _first_line)
        put("applicability", find("Applicability", r".+"), _first_line)

    # ---------------- INSPECTION REPORT ----------------
    elif doc_type == "inspection_report":
        put("report_id", doc_id)
        put("related_work_order", find("Work Order", r"[A-Z0-9\-]+"))
        put("aircraft", find("Aircraft", r".+"), _first_line)
        put("registration", find("Registration", r"[A-Z0-9\-]+"))
        put("date", find("Date", r".+"), normalize_date)
        put("inspector", find("Inspector", r".+"), _first_line)
        put("component", find("Component", r".+"), _first_line)
        put("measurement_value_mm", find("Measured", r"[\d.,]+"), normalize_decimal)
        put("limit_mm", find("Limit", r"[\d.,]+"), normalize_decimal)
        put("applicability", find("Applicability", r".+"), _first_line)

    # ---------------- NON ROUTINE DEFECT ----------------
    elif doc_type == "non_routine_defect":
        put("defect_id", doc_id)
        put("date", find("Date", r".+"), normalize_date)
        put("task_card", find("Task Card", r"TC-\d{2}-\d{2}-\d{3}"))
        put("related_work_order", find("Work Order", r"[A-Z0-9\-]+"))
        put("aircraft", find("Aircraft", r".+"), _first_line)
        put("registration", find("Registration", r"[A-Z0-9\-]+"))
        put("serial_no", find("Serial", r"[A-Z0-9\-]+"))
        put("severity", find("Severity", r".+"), _first_line)
        put("crack_length_mm", find("Crack", r"[\d.,]+"), normalize_decimal)
        put("immediate_action", find("Immediate action", r".+"), _first_line)

    # ---------------- MATERIAL ISSUE NOTE ----------------
    elif doc_type == "material_issue_note":
        put("issue_note", doc_id)
        put("date", find("Date", r".+"), normalize_date)
        put("work_order", find("Work Order", r"[A-Z0-9\-]+"))
        put("location", find("Location", r".+"), _first_line)
        put("supplier", find("Supplier", r".+"), _first_line)
        put("destination", find("Destination", r".+"), _first_line)
        put("part_number", find("Part Number", r"[A-Z0-9\-]+"))
        put("quantity", find("Qty", r"\d+"))
        put("batch_lot", find("Batch", r"[A-Z0-9\-]+"))
        put("carrier", find("Carrier", r".+"), _first_line)

    # ensure all required fields exist
    for k in REQUIRED_FIELDS[doc_type]:
        fields.setdefault(k, "")
        confidence.setdefault(k, 0.0)

    return {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "fields": fields,
        "field_confidence": confidence,
        "extraction_notes": "; ".join(notes[:4]) or "OCR extraction completed.",
    }
