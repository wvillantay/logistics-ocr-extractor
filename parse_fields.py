"""
parse_fields.py
---------------
Takes the raw OCR text (a big messy string) and extracts specific fields
from it using pattern matching (regex) and keyword searching.

Why do we need this?
  OCR gives us a wall of text. This module "makes sense" of that text by
  looking for recognizable patterns like dates, dollar signs, and
  label-value pairs such as "Invoice #: 12345".
"""

import re
import json
import csv
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# REGEX PATTERNS
# Each pattern is a regular expression that matches a specific format.
# re.IGNORECASE means it works whether the text is uppercase or lowercase.
# ---------------------------------------------------------------------------

# Matches dates like: 06/27/2026  |  2026-06-27  |  June 27, 2026  |  27 Jun 2026
# No \b anchors — OCR sometimes glues adjacent characters so word boundaries
# are unreliable. We rely on the digit structure itself to avoid false matches.
DATE_PATTERN = re.compile(
    r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}'               # MM/DD/YYYY or MM-DD-YYYY
    r'|\d{4}[\/\-]\d{2}[\/\-]\d{2}'                    # YYYY-MM-DD
    r'|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}'  # June 27, 2026
    r'|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})',  # 27 Jun 2026
    re.IGNORECASE
)

# Matches invoice or order numbers preceded by a clear label.
# Requires the label to be followed by #, No., or : and then an ID of at
# least 3 characters. Does NOT include "bill" — that word also appears in
# "Bill of Lading" and causes false matches on reference lines.
INVOICE_PATTERN = re.compile(
    r'(?:invoice|order|po)\s*(?:#|no\.?|number|num)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-]{2,})',
    re.IGNORECASE
)

# Matches dollar amounts that include a decimal point and cents.
# Requiring ".XX" at the end avoids matching bare numbers like zip codes or
# product model numbers (e.g. "4070") that happen to appear near a $ sign.
AMOUNT_PATTERN = re.compile(
    r'\$\s?[\d,]+\.\d{2}|USD\s?[\d,]+\.\d{2}'
)

# Matches vendor or customer names introduced by common labels
VENDOR_PATTERN = re.compile(
    r'(?:from|vendor|supplier|sold by|ship from|billed to|customer|consignee)[:\s]+([A-Za-z0-9 ,\.]+)',
    re.IGNORECASE
)

# Matches tracking numbers that follow a clear label.
# Minimum 8 characters prevents short model numbers like "4070" from matching.
TRACKING_PATTERN = re.compile(
    r'(?:tracking|awb|waybill)\s*(?:#|no\.?)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-]{7,})',
    re.IGNORECASE
)

# Matches quantities like: Qty: 5  |  Quantity: 12  |  10 units
QTY_PATTERN = re.compile(
    r'(?:qty|quantity|units?|pcs?|pieces?)[:\s]+(\d+)',
    re.IGNORECASE
)


def detect_document_type(text: str) -> str:
    """
    Guess what kind of document this is based on keywords in the text.

    Returns one of: 'Invoice', 'Packing List', 'Bill of Lading',
                    'Purchase Order', 'Receipt', or 'Unknown'.
    """
    text_lower = text.lower()

    # "Commercial Invoice" must be checked before "Bill of Lading" because a
    # real invoice document often references a B/L number at the bottom, which
    # would cause the old order to misclassify it as a Bill of Lading.
    if "commercial invoice" in text_lower:
        return "Commercial Invoice"
    elif "bill of lading" in text_lower or "b/l" in text_lower:
        return "Bill of Lading"
    elif "packing list" in text_lower or "packing slip" in text_lower:
        return "Packing List"
    elif "purchase order" in text_lower or "p.o." in text_lower:
        return "Purchase Order"
    elif "receipt" in text_lower:
        return "Receipt"
    elif "invoice" in text_lower:
        return "Invoice"
    else:
        return "Unknown"


def extract_line_items(text: str) -> list:
    """
    Try to pull out item rows that look like product lines in a table.
    A "line item" typically has a description followed by a quantity and price.

    This is a simple approach: we look for lines that contain both a number
    and a dollar amount, suggesting they describe a product and its cost.

    Returns a list of strings, each representing one line item.
    """
    items = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        # Skip blank or very short lines
        if len(line) < 5:
            continue
        # If a line has a number AND a dollar sign, it probably describes an item
        has_number = re.search(r'\d', line)
        has_dollar = re.search(r'\$|usd', line, re.IGNORECASE)
        if has_number and has_dollar and len(line) > 10:
            items.append(line)

    return items


def parse_fields(raw_text: str) -> dict:
    """
    Main parsing function. Takes raw OCR text and returns a structured
    dictionary with all the fields we were able to find.

    Args:
        raw_text: The string returned by extract_text.py

    Returns:
        A dictionary like:
        {
          "document_type": "Invoice",
          "date": "06/27/2026",
          "invoice_number": "INV-1001",
          "vendor": "Acme Corp",
          "amounts": ["$1,500.00", "$250.00"],
          "total_amount": "$1,500.00",
          "tracking_number": "1Z999AA10123456784",
          "quantities": ["10", "5"],
          "line_items": ["Widget A  10  $500.00", ...],
          "raw_text_preview": "first 300 characters of raw text..."
        }
    """

    # --- Find document type ---
    doc_type = detect_document_type(raw_text)

    # --- Find all dates, take the first one as the primary date ---
    dates = DATE_PATTERN.findall(raw_text)
    primary_date = dates[0] if dates else "Not found"

    # --- Find invoice or order number ---
    invoice_match = INVOICE_PATTERN.search(raw_text)
    invoice_number = invoice_match.group(1).strip() if invoice_match else "Not found"

    # --- Find vendor or customer name ---
    vendor_match = VENDOR_PATTERN.search(raw_text)
    vendor_name = vendor_match.group(1).strip() if vendor_match else "Not found"

    # --- Find all dollar amounts ---
    amounts = AMOUNT_PATTERN.findall(raw_text)

    # Strategy for finding the total:
    # 1. First look for a line that contains a "total" label AND a dollar amount —
    #    this is the most reliable signal (e.g. "TOTAL AMOUNT DUE: $10,490.43")
    # 2. Fall back to the largest dollar amount found anywhere in the document.
    total_amount = "Not found"
    total_label_pattern = re.compile(
        r'(?:total|amount due|grand total)[^\n]*(\$[\d,]+\.\d{2}|USD[\d,]+\.\d{2})',
        re.IGNORECASE
    )
    total_match = total_label_pattern.search(raw_text)
    if total_match:
        total_amount = total_match.group(1).strip()
    elif amounts:
        # Helper: strip non-numeric characters and convert to float safely
        def to_float(a):
            cleaned = re.sub(r'[^\d.]', '', a)
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        total_amount = max(amounts, key=to_float)

    # --- Find tracking number ---
    tracking_match = TRACKING_PATTERN.search(raw_text)
    tracking_number = tracking_match.group(1).strip() if tracking_match else "Not found"

    # --- Find quantities ---
    quantities = QTY_PATTERN.findall(raw_text)

    # --- Find line items ---
    line_items = extract_line_items(raw_text)

    # --- Build the result dictionary ---
    result = {
        "document_type": doc_type,
        "date": primary_date,
        "invoice_number": invoice_number,
        "vendor": vendor_name,
        "amounts_found": amounts,
        "total_amount": total_amount,
        "tracking_number": tracking_number,
        "quantities": quantities,
        "line_items": line_items,
        "raw_text_preview": raw_text[:300].replace("\n", " ").strip(),
        "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return result


def save_as_json(data: dict, output_path: str) -> str:
    """
    Write the parsed fields dictionary to a JSON file.

    Args:
        data: The dictionary returned by parse_fields()
        output_path: Where to save the .json file

    Returns:
        The path where the file was saved.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        # indent=2 makes the JSON human-readable with nice indentation
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output_path


def save_as_csv(data: dict, output_path: str) -> str:
    """
    Write the parsed fields to a flat CSV file.
    Multi-value fields (like amounts or line items) are joined into one cell
    separated by semicolons so they fit in a single CSV column.

    Args:
        data: The dictionary returned by parse_fields()
        output_path: Where to save the .csv file

    Returns:
        The path where the file was saved.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Flatten list fields into semicolon-separated strings for CSV compatibility
    flat = {
        key: "; ".join(val) if isinstance(val, list) else val
        for key, val in data.items()
    }

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flat.keys())
        writer.writeheader()   # Write the column names on the first row
        writer.writerow(flat)  # Write the data on the second row

    return output_path
