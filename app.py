"""
app.py
------
The Streamlit web application — the main interface for this project.

What is Streamlit?
  Streamlit is a Python library that turns a Python script into a
  browser-based app with just a few lines of code. No HTML or JavaScript
  needed. You run it with: streamlit run app.py

What this app does:
  1. Lets you upload a document image (JPG, PNG, etc.)
  2. Displays the image on screen
  3. Runs OCR to extract the raw text
  4. Parses the text to find structured fields
  5. Shows results in a clean table
  6. Lets you download the results as JSON or CSV
"""

import streamlit as st
from PIL import Image
import json
import io
import os
import pandas as pd

# Import our own modules
from extract_text import extract_text_from_pil
from parse_fields import parse_fields, save_as_json, save_as_csv


# ---------------------------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Logistics OCR Extractor",
    page_icon="📦",
    layout="wide",       # Use the full width of the browser
)


# ---------------------------------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------------------------------

st.title("📦 Logistics OCR Extractor")
st.markdown(
    """
    Upload a logistics document (invoice, packing list, bill of lading, etc.)
    and this tool will extract the text and organize it into structured data.

    > **Powered by:** Python · Tesseract OCR · Streamlit
    """
)
st.divider()


# ---------------------------------------------------------------------------
# SIDEBAR — Settings and instructions
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("How to Use")
    st.markdown(
        """
        1. Click **Browse files** to upload an image
        2. Wait for OCR to finish (a few seconds)
        3. Review the extracted text and parsed fields
        4. Download results as JSON or CSV
        """
    )
    st.divider()
    st.header("Supported Formats")
    st.markdown("- JPG / JPEG\n- PNG\n- BMP\n- TIFF")
    st.divider()
    st.markdown("**Note:** Image quality affects OCR accuracy. Clear, well-lit scans work best.")


# ---------------------------------------------------------------------------
# FILE UPLOAD SECTION
# ---------------------------------------------------------------------------

uploaded_file = st.file_uploader(
    label="Upload a document image",
    type=["jpg", "jpeg", "png", "bmp", "tiff"],
    help="Upload a clear image of your logistics document."
)

# Only run the pipeline if the user has uploaded something
if uploaded_file is not None:

    # --- Display the uploaded image ---
    col1, col2 = st.columns([1, 1])  # Two side-by-side columns

    with col1:
        st.subheader("Uploaded Document")
        pil_image = Image.open(uploaded_file)
        st.image(pil_image, caption=uploaded_file.name, use_column_width=True)

    # --- Run OCR ---
    with st.spinner("Running OCR — extracting text from image..."):
        raw_text = extract_text_from_pil(pil_image)

    # --- Show raw extracted text ---
    with col2:
        st.subheader("Raw Extracted Text")
        if raw_text.strip():
            st.text_area(
                label="OCR Output",
                value=raw_text,
                height=400,
                help="This is exactly what Tesseract read from the image."
            )
        else:
            st.warning(
                "No text was detected. Try a higher-resolution image or "
                "make sure Tesseract is installed correctly."
            )

    st.divider()

    # --- Parse the extracted text into fields ---
    st.subheader("Parsed Fields")

    with st.spinner("Parsing fields from extracted text..."):
        parsed = parse_fields(raw_text)

    # Show the main fields in two clean metric columns
    col3, col4, col5 = st.columns(3)
    col3.metric("Document Type", parsed["document_type"])
    col4.metric("Date", parsed["date"])
    col5.metric("Invoice / Order #", parsed["invoice_number"])

    col6, col7, col8 = st.columns(3)
    col6.metric("Vendor / Customer", parsed["vendor"])
    col7.metric("Total Amount", parsed["total_amount"])
    col8.metric("Tracking #", parsed["tracking_number"])

    # Show all found amounts
    if parsed["amounts_found"]:
        st.markdown(f"**All Amounts Found:** {', '.join(parsed['amounts_found'])}")

    # Show quantities
    if parsed["quantities"]:
        st.markdown(f"**Quantities Found:** {', '.join(parsed['quantities'])}")

    # Show line items in a table if any were found
    if parsed["line_items"]:
        st.subheader("Detected Line Items")
        df_items = pd.DataFrame(parsed["line_items"], columns=["Line Item"])
        st.dataframe(df_items, use_container_width=True)

    st.divider()

    # --- Full parsed data as expandable JSON ---
    with st.expander("View Full Parsed Data (JSON)"):
        st.json(parsed)

    st.divider()

    # --- Download Buttons ---
    st.subheader("Download Results")

    # Prepare JSON string for download
    json_str = json.dumps(parsed, indent=2)
    json_bytes = json_str.encode("utf-8")

    # Prepare CSV for download using a flat representation
    flat = {
        key: "; ".join(val) if isinstance(val, list) else val
        for key, val in parsed.items()
    }
    df_flat = pd.DataFrame([flat])
    csv_buffer = io.StringIO()
    df_flat.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    # Side-by-side download buttons
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
        st.download_button(
            label="⬇️ Download as JSON",
            data=json_bytes,
            file_name="extracted_fields.json",
            mime="application/json",
        )

    with dl_col2:
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_bytes,
            file_name="extracted_fields.csv",
            mime="text/csv",
        )

    # Also save locally to the output/ folder
    base_name = os.path.splitext(uploaded_file.name)[0]
    save_as_json(parsed, f"output/{base_name}.json")
    save_as_csv(parsed, f"output/{base_name}.csv")
    st.caption(f"Results also saved to output/{base_name}.json and output/{base_name}.csv")

else:
    # --- Shown when no file is uploaded yet ---
    st.info("Upload a document image using the button above to get started.")
    st.markdown(
        """
        **Don't have a sample document?**
        Run this in your terminal to generate a fake invoice image:
        ```
        python generate_sample.py
        ```
        Then upload `sample_docs/sample_invoice.png` from this app.
        """
    )

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "Logistics OCR Extractor · Built with Python + Tesseract + Streamlit · "
    "For demonstration and learning purposes only · No real company data used."
)
