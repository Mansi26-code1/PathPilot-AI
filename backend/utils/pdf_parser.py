from pypdf import PdfReader
import re


def clean_text(text: str):

    # Remove single-character lines like:
    # M
    # A
    # N
    lines = text.splitlines()

    cleaned = []

    for line in lines:

        line = line.strip()

        if len(line) == 1:
            continue

        cleaned.append(line)

    text = "\n".join(cleaned)

    # Remove multiple blank lines
    text = re.sub(r"\n{2,}", "\n\n", text)

    return text


def extract_text_from_pdf(file_path: str):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return clean_text(text)