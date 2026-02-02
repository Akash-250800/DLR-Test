from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytesseract

# IMPORTANT: Explicit path for Windows (PATH is not set)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _preprocess(img_bgr: np.ndarray) -> np.ndarray:
    """
    Preprocess scanned documents for better OCR:
    - grayscale
    - upscale
    - denoise
    - adaptive threshold
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # upscale small text
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # denoise + sharpen
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    gray = cv2.filter2D(gray, -1, kernel)

    # adaptive threshold (robust for scanned forms)
    thr = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        7,
    )
    return thr


def ocr_image(image_path: Path) -> str:
    """
    OCR from image -> text using pytesseract.

    Returns:
        OCR text as a single string.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    processed = _preprocess(img)

    # LSTM OCR engine, block-of-text mode
    config = "--oem 3 --psm 6"
    return pytesseract.image_to_string(processed, config=config)

