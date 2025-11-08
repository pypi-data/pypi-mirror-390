from .pdf_llm_parser.google_gemini_parser import analyze_document as google_analyze_document


def analyze_document(pdf_binary: bytes, api_key=None, model: str = None, prompt=None) -> dict:
    return google_analyze_document(pdf_binary, api_key=api_key, model=model, prompt=prompt)
