ALLOWED_TYPES = {"task_card", "inspection_report", "non_routine_defect", "material_issue_note"}

REQUIRED_BY_TYPE = {
    "task_card": {
        "task_card_no","work_order","aircraft_type","registration","serial_no",
        "ata_chapter","location","date","interval","applicability"
    },
    "inspection_report": {
        "report_id","related_work_order","aircraft","registration","date","inspector",
        "component","measurement_value_mm","limit_mm","applicability"
    },
    "non_routine_defect": {
        "defect_id","date","task_card","related_work_order","aircraft","registration",
        "serial_no","severity","crack_length_mm","immediate_action"
    },
    "material_issue_note": {
        "issue_note","date","work_order","location","supplier","destination",
        "part_number","quantity","batch_lot","carrier"
    },
}

def validate_obj(obj):
    assert obj.get("doc_id")
    assert obj.get("doc_type") in ALLOWED_TYPES
    assert isinstance(obj.get("fields"), dict)
    assert isinstance(obj.get("field_confidence"), dict)

    assert set(obj["fields"].keys()) == set(obj["field_confidence"].keys())
    for v in obj["field_confidence"].values():
        assert 0.0 <= float(v) <= 1.0

    missing = REQUIRED_BY_TYPE[obj["doc_type"]] - set(obj["fields"].keys())
    assert not missing, f"Missing fields: {missing}"

def test_schema_smoke():
    sample = {
        "doc_id": "X",
        "doc_type": "task_card",
        "fields": {k: "x" for k in REQUIRED_BY_TYPE["task_card"]},
        "field_confidence": {k: 0.5 for k in REQUIRED_BY_TYPE["task_card"]},
        "extraction_notes": ""
    }
    validate_obj(sample)
