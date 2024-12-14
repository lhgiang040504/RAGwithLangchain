import re
from underthesea import text_normalize
from langchain_community.document_loaders import PyPDFLoader

def extract_answer(text_response: str, pattern: str = r'Answer:\s*(.*)') -> str:
    match = re.search(pattern, text_response)

    if match:
        answer_text = match.group(1).strip()
    else:
        return "Answer not found"

def normalize(text):
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    text = text_normalize(text)

    return text

def read_pdf(file_location):
    loader = PyPDFLoader(file_location)
    text = ''
    for doc in loader.lazy_load():
        text += normalize(doc.page_content)
    
    return text

def remove_non_utf8_characters(text):
    return ''.join(char for char in text if ord(char) < 128)

def load_pdf(pdf_file):
    docs = PyPDFLoader(pdf_file, extract_images=True).load()
    text = ''
    for doc in docs:
        text += remove_non_utf8_characters(doc.page_content)

    return text