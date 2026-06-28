# Learning Notes — What I Learned Building This Project

## 1. What is OCR?

**OCR** stands for **Optical Character Recognition**.

It is a technology that looks at an image (like a photo of a document) and converts the visual text it "sees" into a real, editable text string that Python can work with.

**Analogy:** Imagine you took a photo of a handwritten note. A human can read it, but Python can't — Python only sees pixels. OCR is the bridge that teaches Python to "read" those pixels as characters.

### How pytesseract works:
1. You give it an image (JPG, PNG, etc.)
2. Tesseract (the underlying engine, originally built by HP and now maintained by Google) analyzes the shapes of characters in the image
3. It returns a string with all the text it recognized

```python
import pytesseract
from PIL import Image

image = Image.open("invoice.png")
text = pytesseract.image_to_string(image)
print(text)  # Prints the text found in the image
```

### Why grayscale?
Converting to grayscale (black and white) removes color noise and makes character edges clearer. This improves OCR accuracy, especially on printed documents.

---

## 2. What is Regex (Regular Expressions)?

**Regex** is a mini-language for describing text patterns.

Instead of checking every possible date format manually, you write one pattern that matches all of them.

### Example — matching a date:
```python
import re

pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
text = "Invoice Date: 06/27/2026"

match = pattern.search(text)
print(match.group())  # Output: 06/27/2026
```

### Regex symbols I used:
| Symbol | Meaning |
|--------|---------|
| `\d`   | Any digit (0–9) |
| `{1,2}` | Between 1 and 2 of the previous character |
| `\b`   | Word boundary (prevents partial matches) |
| `\|`   | OR — match this pattern OR that one |
| `(?:...)` | Non-capturing group — group without saving |
| `[...]` | Character class — match any one of these |
| `*` | Zero or more of the previous character |
| `+` | One or more of the previous character |
| `?` | Zero or one (makes something optional) |

---

## 3. What is JSON and why use it?

**JSON** (JavaScript Object Notation) is a text-based format for storing structured data. It looks like a Python dictionary.

```json
{
  "document_type": "Invoice",
  "date": "06/27/2026",
  "invoice_number": "INV-2026-1042",
  "total_amount": "$10,490.43"
}
```

### Why JSON for this project?
- Easy for humans to read
- Easy for other programs to read (APIs, databases, dashboards)
- Python's `json` module handles it natively
- Standard format used in logistics software, ERPs, and APIs

---

## 4. What is CSV and why use it?

**CSV** (Comma-Separated Values) is a plain-text format where each row is a line and columns are separated by commas.

```
document_type,date,invoice_number,total_amount
Invoice,06/27/2026,INV-2026-1042,$10,490.43
```

### Why CSV?
- Opens directly in Excel or Google Sheets
- Easy to import into databases
- Lightweight and universally supported
- Great for reporting and data analysis

---

## 5. What is Streamlit?

Streamlit is a Python library that converts a Python script into a browser-based web app.

Before Streamlit existed, building a web interface required learning HTML, CSS, JavaScript, and a web framework. Streamlit removes all that — you write pure Python and get a working app.

```python
import streamlit as st

st.title("My App")
file = st.file_uploader("Upload a file")
if file:
    st.write("You uploaded:", file.name)
```

Run with: `streamlit run app.py`

---

## 6. Key concepts for logistics automation

| Concept | What it means in logistics |
|---------|---------------------------|
| **OCR** | Digitize paper invoices, packing slips, and labels |
| **Parsing** | Pull out PO numbers, dates, quantities from unstructured text |
| **JSON output** | Feed structured data into ERP, WMS, or TMS systems |
| **CSV output** | Import into Excel or upload to databases for reporting |
| **Document AI** | Automate data entry that previously required manual labor |

---

## 7. Limitations I learned about

- **OCR accuracy depends heavily on image quality.** A blurry scan will produce garbled text.
- **Regex is brittle.** If the document format changes, patterns may need to be updated.
- **Tesseract struggles with complex layouts** — tables, columns, and rotated text can confuse it.
- **Handwritten text** is not well-supported by pytesseract. For handwriting, you would need a deep-learning model or Google Document AI / AWS Textract.
- **Real production systems** use cloud APIs like Google Cloud Vision or AWS Textract for much higher accuracy.

---

## 8. What I would add next

1. **Better table extraction** — use `pytesseract.image_to_data()` to get bounding boxes around each word
2. **Multiple pages** — process PDFs by converting each page to an image with `pdf2image`
3. **Cloud OCR** — replace Tesseract with Google Cloud Vision API for better accuracy
4. **Database storage** — save results to SQLite instead of flat files
5. **Batch processing** — process a whole folder of documents at once
