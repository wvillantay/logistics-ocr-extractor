"""
generate_sample.py
------------------
Creates a fake logistics invoice image using only Pillow (PIL).
No real company data. Run this once to create a sample you can test with.

Usage:
    python generate_sample.py

Output:
    sample_docs/sample_invoice.png
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Where to save the generated image
OUTPUT_PATH = "sample_docs/sample_invoice.png"

# ---------------------------------------------------------------------------
# FAKE INVOICE DATA (all fictional)
# ---------------------------------------------------------------------------

INVOICE_LINES = [
    ("COMMERCIAL INVOICE", True, 28),
    ("", False, 14),
    ("Vendor:       Acme Logistics Co., 123 Warehouse Ave, Los Angeles CA 90001", False, 14),
    ("Customer:     TechRetail Inc., 456 Commerce Blvd, Diamond Bar CA 91765", False, 14),
    ("", False, 14),
    ("Invoice #:    INV-2026-1042", False, 15),
    ("Order #:      PO-88571", False, 15),
    ("Date:         06/27/2026", False, 15),
    ("Tracking #:   1Z999AA10123456784", False, 15),
    ("", False, 14),
    ("-" * 72, False, 13),
    ("ITEM DESCRIPTION                  QTY    UNIT PRICE    TOTAL", False, 13),
    ("-" * 72, False, 13),
    ("Newegg RTX 4070 GPU (12GB VRAM)   Qty: 10   $599.99    $5,999.90", False, 14),
    ("Newegg B550M Motherboard           Qty: 5    $149.99      $749.95", False, 14),
    ("Newegg 1TB NVMe SSD                Qty: 20    $89.99    $1,799.80", False, 14),
    ("Newegg 32GB DDR5 RAM Kit           Qty: 8    $119.99      $959.92", False, 14),
    ("-" * 72, False, 13),
    ("", False, 14),
    ("Subtotal:                                              $9,509.57", False, 14),
    ("Shipping:                                                $125.00", False, 14),
    ("Tax (9%):                                                $855.86", False, 14),
    ("", False, 14),
    ("TOTAL AMOUNT DUE:                                     $10,490.43", True, 16),
    ("", False, 14),
    ("-" * 72, False, 13),
    ("Bill of Lading Reference: BOL-2026-77321", False, 13),
    ("Packing List: PL-2026-1042", False, 13),
    ("Terms: Net 30  |  Currency: USD", False, 13),
    ("Thank you for your business!", False, 13),
]


def generate_invoice():
    """Draw the fake invoice and save it as a PNG image."""

    # Create a white image (1000 wide x 900 tall pixels)
    width, height = 1000, 950
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Try to use a monospace font; fall back to default if not available
    try:
        font_normal = ImageFont.truetype("cour.ttf", 14)   # Courier on Windows
        font_bold   = ImageFont.truetype("courbd.ttf", 28)
        font_medium = ImageFont.truetype("courbd.ttf", 16)
    except OSError:
        # Default PIL font — no bold or size options, but always available
        font_normal = ImageFont.load_default()
        font_bold   = font_normal
        font_medium = font_normal

    # Add a thin border around the page
    draw.rectangle([(15, 15), (width - 15, height - 15)], outline=(0, 0, 0), width=2)

    # Draw each line of text
    y = 35          # Starting Y position
    margin = 35     # Left margin in pixels

    for line_text, is_header, font_size in INVOICE_LINES:
        # Pick font
        if is_header and font_size >= 20:
            font = font_bold
        elif is_header:
            font = font_medium
        else:
            font = font_normal

        # Header lines are centered; others are left-aligned
        if is_header and font_size >= 20:
            bbox = draw.textbbox((0, 0), line_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
        else:
            x = margin

        draw.text((x, y), line_text, fill=(0, 0, 0), font=font)

        # Move down for the next line
        y += font_size + 6

    # Save the image
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    image.save(OUTPUT_PATH)
    print(f"Sample invoice saved to: {OUTPUT_PATH}")
    print("You can now upload this file in the Streamlit app.")


if __name__ == "__main__":
    generate_invoice()
