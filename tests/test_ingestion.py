from pathlib import Path
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text

pdf_path = Path("data/contracts/sample.pdf")

docs = load_pdf(pdf_path)
cleaned_docs = [clean_text(d) for d in docs]

print(cleaned_docs[0])
