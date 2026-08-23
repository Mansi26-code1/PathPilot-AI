from backend.utils.pdf_parser import extract_text_from_pdf
from backend.services.resume_parser import parse_resume
from backend.services.resume_extractor import extract_resume
import json

text = extract_text_from_pdf("uploads/Mansi_resume (3).pdf")
sections = parse_resume(text)
result = extract_resume(text, sections)

print(json.dumps(result, indent=2, ensure_ascii=False))