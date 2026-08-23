from backend.utils.pdf_parser import extract_text_from_pdf

text = extract_text_from_pdf("uploads/Mansi_resume (3).pdf")

print(text)