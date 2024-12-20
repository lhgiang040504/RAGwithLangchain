from langchain_community.document_loaders import PyPDFLoader

def remove_non_utf8_characters(text):
    return ''.join(char for char in text if ord(char) < 128)

def load_pdf(pdf_file):
    docs = PyPDFLoader(pdf_file, extract_images=True).load()
    text = ''
    for doc in docs:
        text += remove_non_utf8_characters(doc.page_content)

    return text

def load_txt(txt_file):
    """Load and process content from a TXT file."""
    with open(txt_file, 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
    return remove_non_utf8_characters(text)