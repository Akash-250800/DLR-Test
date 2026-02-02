import json
from pathlib import Path

from .extract import extract_fields
from .ocr import ocr_image


def run_pipeline(manifest_path: Path, images_dir: Path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = []
    for fn in manifest["graded_files"]:
        img_path = images_dir / fn
        text = ocr_image(img_path)
        results.append(extract_fields(fn, text))
    return results
