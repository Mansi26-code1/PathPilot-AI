from backend.utils.pdf_parser import extract_text_from_pdf
from backend.services.resume_parser import parse_resume

text = extract_text_from_pdf("uploads/Mansi_resume (3).pdf")

data = parse_resume(text)

for section, values in data.items():

    print("\n" + "=" * 50)
    print(section.upper())
    print("=" * 50)

    if isinstance(values, list):
        for value in values:
            print(value)
    else:
        print(values)