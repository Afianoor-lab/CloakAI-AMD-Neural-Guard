import PyPDF2
from docx import Document
import io
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# --- Naya Code (PDF/DOCX Extraction) ---
def extract_text_from_file(uploaded_file):
    """File type ke mutabiq text extract karne ka function"""
    filename = uploaded_file.name.lower()
    
    try:
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        
        elif filename.endswith('.docx'):
            doc = Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        
        else: # .txt ya digar files ke liye
            return uploaded_file.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"Error reading {filename}: {str(e)}"
# ---------------------------------------

# AI Engines ko initialize karein
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def cloak_sensitive_data(text):
    # 1. Analyze: AI text parh kar sensitive entities dhoonde ga
    # entities list khali rakhne ka matlab hai ye default (Names, Emails, Phone, etc.) sab dhoonde ga
    analysis_results = analyzer.analyze(text=text, entities=[], language='en')

    # 2. Anonymize: Jo data mila hai usay mask (chupana) karna
    # Yahan hum define kar rahe hain ke kaunsa data kaise nazar aaye
    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "[NAME_CLOAKED]"}),
        "EMAIL_ADDRESS": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 15, "from_end": False}),
        "PHONE_NUMBER": OperatorConfig("mask", {"masking_char": "X", "chars_to_mask": 7, "from_end": True}),
        "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION_SECURED]"}),
    }

    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analysis_results,
        operators=operators
    )

    return anonymized_result.text