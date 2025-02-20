import pdfplumber
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a single PDF file and returns it as a string."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        if not text:
            print(f"⚠️ No text found in {pdf_path}")
    except Exception as e:
        print(f"❌ Error extracting text from {pdf_path}: {e}")
    
    return text.strip()

# Example usage
if __name__ == "__main__":
    sample_pdf = "uploaded_reports/sample.pdf"
    if os.path.exists(sample_pdf):
        extracted_text = extract_text_from_pdf(sample_pdf)
        print("📄 Extracted Text:", extracted_text[:500])  # Print first 500 characters
    else:
        print("⚠️ Sample PDF not found!")


