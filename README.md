# 📦 Logistics OCR Extractor

A small Python learning project that extracts text from logistics document images and parses the results into structured JSON and CSV output.

I built this to get hands-on experience with OCR, regex parsing, and Streamlit while exploring how document automation works in warehouse and e-commerce environments. This is a beginner prototype — not a production system — but it does work end-to-end on a sample invoice.

---

## Demo Screenshot

![Logistics OCR Extractor demo](screenshots/demo_screenshot.PNG)

---

## What it does

1. **Upload** a document image (invoice, packing list, shipping form, etc.)
2. **Extract** all visible text using Tesseract OCR
3. **Parse** the text to find key fields:
   - Document type
   - Date
   - Invoice / Order number
   - Vendor / Customer name
   - Line items and quantities
   - Dollar amounts and totals
   - Tracking number
4. **Export** the structured result as JSON and CSV
5. **View** everything in a Streamlit web interface running in the browser

---

## Why I built this

Warehouses and logistics companies deal with a lot of paper — invoices, packing slips, bills of lading — and someone has to manually read and key that data into a system. OCR can digitize that first step.

I wanted to understand how that pipeline actually works at a code level: how do you go from an image to clean structured data? This project is my attempt to build the simplest version of that from scratch.

---

## Tools used

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Core language |
| **pytesseract** | Python wrapper around the Tesseract OCR engine |
| **Pillow (PIL)** | Opens and preprocesses images before OCR |
| **re (regex)** | Pattern matching to extract dates, amounts, IDs from raw text |
| **Streamlit** | Turns the Python script into a browser-based app |
| **pandas** | DataFrame creation and CSV export |
| **json** | Built-in Python module for saving structured output |

---

## What I learned

Some things I ran into while building this that I didn't fully expect:

- **pytesseract is just a wrapper.** You also have to install the actual Tesseract binary on your system separately. On Windows, `pip install pytesseract` alone is not enough — I had to download the installer from UB Mannheim and then point Python to the `.exe` path in the code.
- **Tesseract does not get added to PATH automatically on Windows.** I had to hardcode the install path in `extract_text.py` to get it working:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```
- **Streamlit version matters.** I hit a `TypeError` on `st.image()` because `use_container_width` was not available in the installed version. I had to switch to the older `use_column_width=True` parameter.
- **OCR output is messier than expected.** Even on a clean generated image, Tesseract sometimes collapses spaces, misreads punctuation, or breaks lines unexpectedly. The raw text is not always what you'd type yourself.
- **Regex parsing can grab the wrong thing easily.** My invoice number pattern was matching street numbers from the vendor address. My tracking number pattern was matching "4070" from a GPU product name. I had to narrow the patterns significantly — requiring minimum character lengths, requiring labeled prefixes, requiring decimal cents on dollar amounts — before the results made sense.
- **Production document AI is much more than OCR + regex.** Real systems need layout analysis (understanding table structure, bounding boxes, column alignment), output validation (does this total match the line items?), confidence scores, and a human review queue for low-confidence extractions. This project only scratches the surface of that.

---

## Project structure

```
logistics-ocr-extractor/
│
├── app.py                  ← Streamlit web app (run this)
├── extract_text.py         ← OCR logic
├── parse_fields.py         ← Field extraction logic
├── generate_sample.py      ← Creates a fake invoice image for testing
├── requirements.txt        ← Python dependencies
│
├── sample_docs/            ← Place test images here
├── output/                 ← JSON and CSV results saved here
├── screenshots/            ← App screenshots
│
└── docs/
    ├── learning_notes.md       ← Explains OCR, regex, JSON, CSV, Streamlit
    ├── project_walkthrough.md  ← Every file explained
    └── interview_explanation.md ← How to explain this project
```

---

## Setup and installation

### Prerequisites

1. **Python 3.10 or higher** — [python.org](https://www.python.org/downloads/)

2. **Tesseract OCR binary** — pytesseract is only the Python wrapper; you also need the actual Tesseract program installed separately:
   - **Windows:** Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). Default install path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - **macOS:** `brew install tesseract`
   - **Linux:** `sudo apt install tesseract-ocr`

3. On Windows, Tesseract likely won't be on your PATH. The code in `extract_text.py` already handles this by pointing directly to the install location — just make sure Tesseract is installed at the default path.

### Install Python dependencies

```bash
git clone https://github.com/wvillantay/logistics-ocr-extractor.git
cd logistics-ocr-extractor
pip install -r requirements.txt
```

### Generate a sample document

No real document needed. Run this to create a fictional invoice image:

```bash
python generate_sample.py
```

This saves `sample_docs/sample_invoice.png` — a fake invoice with made-up vendor names, products, and amounts.

### Run the app

```bash
streamlit run app.py
```

Open your browser to **http://localhost:8501**, upload the sample invoice, and see the extracted fields.

---

## Example output

**JSON (`output/sample_invoice.json`):**
```json
{
  "document_type": "Commercial Invoice",
  "date": "06/27/2026",
  "invoice_number": "INV-2026-1042",
  "vendor": "Acme Logistics Co.",
  "total_amount": "$10,490.43",
  "tracking_number": "1Z999AA10123456784",
  "quantities": ["10", "5", "20", "8"],
  "parsed_at": "2026-06-27 10:30:00"
}
```

**CSV (`output/sample_invoice.csv`):**
```
document_type,date,invoice_number,vendor,total_amount,tracking_number
Commercial Invoice,06/27/2026,INV-2026-1042,Acme Logistics Co.,$10,490.43,1Z999AA10123456784
```

---

## Limitations

This is a beginner prototype. It works on the sample document, but there are real limitations worth knowing:

- **Image quality matters a lot.** A blurry or skewed scan will produce garbage OCR output. Tesseract is sensitive to image resolution and alignment.
- **Regex is fragile.** Patterns that work for one document layout may break on another. I had to fix several false matches during development when patterns grabbed the wrong numbers from the document.
- **OCR errors carry forward.** If Tesseract misreads `$10,490.43` as `$10.490.43`, the parser gets a bad value with no way to know. There's no error correction layer here.
- **No output validation.** The code doesn't check whether results are plausible — for example, whether the parsed total matches the sum of line items.
- **No PDF support.** PDFs need to be converted to images first (e.g. with `pdf2image`).
- **No handwriting support.** Tesseract is built for printed text.
- **One file at a time.** Batch processing is not implemented.

For a real production system, you'd replace Tesseract with a cloud service like **Google Cloud Document AI**, **AWS Textract**, or **Azure Form Recognizer**, and add layout analysis, confidence scoring, and a human review step. This project is a foundation for understanding what those systems are actually doing.

---

## Possible next steps

- [ ] Add PDF support via `pdf2image`
- [ ] Add batch folder processing
- [ ] Swap Tesseract for Google Cloud Vision API
- [ ] Store results in SQLite instead of flat files
- [ ] Add confidence scores and flag low-confidence extractions for review

---

## Disclaimer

All sample documents are entirely fictional. No real company names, invoice numbers, or personal data are used. This project is for learning and portfolio purposes only.

---

## Author

[William Villantay](https://github.com/wvillantay) — learning Python, OCR, and document AI.
