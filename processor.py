import PyPDF2
from docx import Document
import io
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# --- PDF/DOCX Extraction ---
def extract_text_from_file(uploaded_file):
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
        else:
            return uploaded_file.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"Error reading {filename}: {str(e)}"

# --- AI Engines Initialization ---
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# --- 1. CUSTOM REGEX PATTERNS FOR CYBER TOKENS & SECURITY DATA ---
# Universal API/Auth Token Regex (gsk_, sk-, JWT patterns, and common hex/alphanumeric secrets)
cyber_key_pattern = Pattern(
    name="cyber_key_pattern",
    regex=r'(?i)(?:gsk_[a-zA-Z0-9]{32,64}|sk-[a-zA-Z0-9]{32,64}|(?<=[:=,\'\"]\s)[a-zA-Z0-9_-]{24,64}(?=[\s\'\"]|$))',
    score=0.95
)
api_key_recognizer = PatternRecognizer(
    supported_entity="API_KEY",
    patterns=[cyber_key_pattern],
    context=["key", "api", "token", "secret", "password", "groq", "openai", "gsk", "credential", "auth"]
)
analyzer.registry.add_recognizer(api_key_recognizer)

# Custom Pakistani CNIC pattern support
cnic_pattern = Pattern(
    name="cnic_pattern",
    regex=r'\b\d{5}-\d{7}-\d{1}\b',
    score=0.95
)
cnic_recognizer = PatternRecognizer(
    supported_entity="CNIC",
    patterns=[cnic_pattern],
    context=["cnic", "identity", "passport", "card", "identity number"]
)
analyzer.registry.add_recognizer(cnic_recognizer)


# --- 2. THE MAIN CLOAKING FUNCTION ---
def cloak_sensitive_data(text):
    # Enforce standard language analysis
    analysis_results = analyzer.analyze(text=text, language='en')

    # Complete Operators dictionary matching EVERY single UI checkbox entity
    operators = {
        # --- IDENTIFIERS (PII) ---
        "PERSON": OperatorConfig("replace", {"new_value": "[NAME_CLOAKED]"}),
        "EMAIL_ADDRESS": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 15, "from_end": False}),
        "PHONE_NUMBER": OperatorConfig("mask", {"masking_char": "X", "chars_to_mask": 7, "from_end": True}),
        "CNIC": OperatorConfig("replace", {"new_value": "[GOVT_ID_CLOAKED]"}),
        "US_PASSPORT": OperatorConfig("replace", {"new_value": "[PASSPORT_SECURED]"}),
        
        # --- FINANCIAL (PCI) ---
        "CREDIT_CARD": OperatorConfig("mask", {"masking_char": "X", "chars_to_mask": 12, "from_end": False}),
        "IBAN_CODE": OperatorConfig("replace", {"new_value": "[IBAN_SECURED]"}),
        "US_BANK_NUMBER": OperatorConfig("replace", {"new_value": "[BANK_ACCOUNT_CLOAKED]"}),
        "TAX_RECOGNIZER": OperatorConfig("replace", {"new_value": "[TAX_ID_CLOAKED]"}), # Matches general tax patterns
        
        # --- CYBER ---
        "IP_ADDRESS": OperatorConfig("replace", {"new_value": "[IP_ADDRESS_MASKED]"}),
        "API_KEY": OperatorConfig("replace", {"new_value": "[API_KEY_CLOAKED]"}),
    }

    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analysis_results,
        operators=operators
    )

    return anonymized_result.text