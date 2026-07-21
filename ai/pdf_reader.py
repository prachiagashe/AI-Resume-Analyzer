import PyPDF2

def extract_text(pdf_path):
    """
    Reads the uploaded PDF resume and extracts text from all pages.
    
    Args:
        pdf_path (str): The file path to the PDF.
        
    Returns:
        str: Extracted text from the complete resume.
    """
    extracted_text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + " "
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        
    return extracted_text.strip()
