import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re

# ✅ Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            page_text = page.get_text("text")
            text += page_text

        # ✅ Force OCR if Passport Number is missing
        if not text.strip() or "Candidate ID" not in text:
            print(f"⚠️ No Candidate ID found in {pdf_path}! Using OCR on images...")
            for page_num in range(len(doc)):
                img = page_to_image(doc, page_num)
                extracted_text = pytesseract.image_to_string(img)
                text += extracted_text

        return text.strip() if text else "OCR Failed"
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return "OCR Failed"

# ✅ Convert PDF page to image for OCR
def page_to_image(doc, page_num):
    page = doc[page_num]
    pix = page.get_pixmap()
    img = Image.open(io.BytesIO(pix.tobytes("ppm")))
    return img

# ✅ Extract IELTS details
def extract_ielts_details(text):
    extracted_data = {}

    # **Debugging: Print Extracted Text**
    print("\n🔍 Extracted Text for Debugging:\n", text)

    # **Extract Passport Number (Candidate ID)**
    passport_match = re.search(r'(?:Passport No|Candidate ID)[:\s]*([A-Za-z0-9]+)', text, re.IGNORECASE)
    extracted_data["passport_number"] = passport_match.group(1) if passport_match else "OCR Failed"

    # **Extract Center Number**
    center_number_match = re.search(r'Centre Number[:\s]*([A-Za-z0-9]+)', text, re.IGNORECASE)
    extracted_data["center_number"] = center_number_match.group(1) if center_number_match else "OCR Failed"

    # **Extract IELTS Scores**
    for key, pattern in {
        "listening": r'Listening[:\s]+(\d+\.\d+)',
        "reading": r'Reading[:\s]+(\d+\.\d+)',
        "writing": r'Writing[:\s]+(\d+\.\d+)',
        "speaking": r'Speaking[:\s]+(\d+\.\d+)',
    }.items():
        match = re.search(pattern, text)
        extracted_data[key] = match.group(1) if match else "OCR Failed"

    return extracted_data

# ✅ File Path for IELTS PDF
ielts_pdf_path = "IELTS.pdf"

# ✅ Extract Text from IELTS PDF
ielts_text = extract_text_from_pdf(ielts_pdf_path)

# ✅ Extract IELTS Details
ielts_details = extract_ielts_details(ielts_text)

# ✅ Print Only Extracted Fields
print("\n📄 **Extracted IELTS Details:**")
print(ielts_details)
