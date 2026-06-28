# Project Walkthrough — Every File Explained

This document walks through each file in the project and explains exactly what it does, why it exists, and how it connects to the other files.

---

## Project Structure

```
logistics-ocr-extractor/
│
├── app.py                  ← Streamlit web app (main entry point)
├── extract_text.py         ← OCR logic (reads text from images)
├── parse_fields.py         ← Parsing logic (finds dates, amounts, etc.)
├── generate_sample.py      ← Creates a fake invoice image for testing
├── requirements.txt        ← Python packages to install
│
├── sample_docs/            ← Put your test images here
├── output/                 ← JSON and CSV files are saved here
├── screenshots/            ← Screenshots of the running app
│
└── docs/
    ├── learning_notes.md       ← What OCR, regex, JSON, CSV, Streamlit are
    ├── project_walkthrough.md  ← This file
    └── interview_explanation.md ← How to explain this in an interview
```

---

## How the files connect

```
User uploads image
       │
       ▼
   app.py  ──────────────────────────────────────┐
       │                                          │
       ▼                                          ▼
extract_text.py                            parse_fields.py
(runs OCR → raw text)          (raw text → structured dict)
                                                  │
                                          ┌───────┴────────┐
                                          ▼                ▼
                                     output/*.json    output/*.csv
```

---

## File-by-file breakdown

### `app.py` — The Web Interface

**What it does:**
This is the main file you run. It creates a browser-based interface using Streamlit where you can upload a document image, see the OCR results, view parsed fields, and download the output.

**Key Streamlit functions used:**
- `st.file_uploader()` — creates the upload button
- `st.image()` — displays the uploaded image
- `st.text_area()` — shows the raw OCR text
- `st.metric()` — shows each parsed field in a clean card
- `st.download_button()` — allows downloading JSON or CSV
- `st.columns()` — arranges content side-by-side

**How to run it:**
```bash
streamlit run app.py
```
Then open your browser to http://localhost:8501

---

### `extract_text.py` — OCR Engine Wrapper

**What it does:**
Contains two functions that use pytesseract to extract text from images.

**Functions:**
1. `extract_text_from_image(image_path)` — takes a file path, opens the image, runs OCR
2. `extract_text_from_pil(pil_image)` — takes an already-opened PIL image object (used by the Streamlit app because uploaded files arrive as PIL objects)

**Why two functions?**
The Streamlit app gets images as PIL objects from `st.file_uploader()`. If you run the project from the command line, you'll have a file path. Having both functions makes the module flexible.

**Key step — grayscale conversion:**
```python
image = image.convert("L")
```
"L" means luminance (black and white). This improves OCR accuracy on printed documents.

---

### `parse_fields.py` — Field Extraction

**What it does:**
This is where the "intelligence" of the project lives. It takes the raw wall of text from OCR and finds specific fields using regex patterns and keyword searches.

**Key functions:**
1. `detect_document_type(text)` — looks for keywords like "invoice", "packing list", "bill of lading"
2. `extract_line_items(text)` — finds lines that look like product rows (have both a number and a dollar sign)
3. `parse_fields(text)` — the main function; calls all the others and returns a complete dictionary
4. `save_as_json(data, path)` — writes the dictionary to a .json file
5. `save_as_csv(data, path)` — writes the dictionary to a .csv file

**How regex patterns work here:**
```python
DATE_PATTERN = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b')
```
This finds dates like 06/27/2026 or 06-27-2026. The `\b` markers mean "word boundary" — they prevent partial matches inside longer strings.

---

### `generate_sample.py` — Sample Document Creator

**What it does:**
Uses Pillow (PIL) to draw a fake invoice as a PNG image and saves it to `sample_docs/sample_invoice.png`.

**Why does this exist?**
You need a test document to run the project, but we cannot include real invoices or company data. This script generates a completely fictional invoice with fake vendor names, products, and amounts — safe to share publicly on GitHub.

**How to run it:**
```bash
python generate_sample.py
```

---

### `requirements.txt` — Dependencies

Lists every Python package the project needs. When someone clones the project, they run:
```bash
pip install -r requirements.txt
```
This installs all packages at once.

**Important note about Tesseract:**
`pytesseract` is a Python *wrapper* around the Tesseract *binary* (a separate program). You must install both:
- The Python package: `pip install pytesseract`
- The Tesseract binary: https://github.com/UB-Mannheim/tesseract/wiki (Windows)

---

### `sample_docs/` — Test Images

Put any document images here for testing. The `generate_sample.py` script saves its output here automatically.

---

### `output/` — Results

When you process a document through the Streamlit app, the JSON and CSV results are automatically saved here with the same base name as the uploaded file.

Example: Upload `invoice_june.png` → Get `output/invoice_june.json` and `output/invoice_june.csv`

---

### `screenshots/` — App Screenshots

Place screenshots of the running Streamlit app here. These are used in the README to show GitHub visitors what the project looks like without them needing to run it.

---

## Data flow step by step

1. User opens browser at `http://localhost:8501` (from `streamlit run app.py`)
2. User uploads `sample_invoice.png`
3. `app.py` receives the file as a PIL Image object
4. `app.py` calls `extract_text_from_pil(pil_image)` from `extract_text.py`
5. `extract_text.py` converts the image to grayscale and runs `pytesseract.image_to_string()`
6. The raw text string is returned to `app.py`
7. `app.py` calls `parse_fields(raw_text)` from `parse_fields.py`
8. `parse_fields.py` runs regex patterns on the text and builds a dictionary
9. The dictionary is returned to `app.py`
10. `app.py` displays the fields on screen using Streamlit
11. `app.py` calls `save_as_json()` and `save_as_csv()` to write files to `output/`
12. User can click Download buttons to get the files
