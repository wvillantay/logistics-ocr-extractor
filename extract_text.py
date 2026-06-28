"""
extract_text.py
---------------
Handles all OCR (Optical Character Recognition) logic.
Given an image file, this module returns the raw text found in it.

What is OCR?
  OCR is a technology that "reads" an image and converts the visual text
  it sees into a plain Python string. Think of it like a scanner that
  turns a photo of a document into editable text.
"""

import pytesseract
from PIL import Image
import os

# Point pytesseract directly at the Tesseract binary on Windows.
# This is needed when the Tesseract install folder is not in the system PATH.
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_image(image_path: str) -> str:
    """
    Open an image file and extract all visible text using Tesseract OCR.

    Args:
        image_path: Full or relative path to the image (JPG, PNG, etc.)

    Returns:
        A single string containing all the text Tesseract found in the image.
        Returns an error message string if something goes wrong.
    """

    # --- Step 1: Confirm the file actually exists before trying to open it ---
    if not os.path.exists(image_path):
        return f"ERROR: File not found at path: {image_path}"

    # --- Step 2: Open the image using Pillow (PIL) ---
    # Pillow converts the file into a format pytesseract can read.
    image = Image.open(image_path)

    # --- Step 3: (Optional) Convert to grayscale to improve OCR accuracy ---
    # Black-and-white images are easier for Tesseract to read than color ones.
    image = image.convert("L")

    # --- Step 4: Run Tesseract OCR on the image ---
    # image_to_string() is the main pytesseract function.
    # It returns all the text it detected as one big string.
    raw_text = pytesseract.image_to_string(image)

    return raw_text


def extract_text_from_pil(pil_image) -> str:
    """
    Same as extract_text_from_image but accepts a PIL Image object directly.
    This is used by the Streamlit app, which loads uploads as PIL images.

    Args:
        pil_image: A PIL Image object (already opened, not a file path).

    Returns:
        Extracted text as a string.
    """

    # Convert to grayscale for better OCR accuracy
    image = pil_image.convert("L")

    # Run OCR and return the resulting text
    raw_text = pytesseract.image_to_string(image)

    return raw_text
