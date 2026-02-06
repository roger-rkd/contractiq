from pathlib import Path
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.chunking.clause_chunker import clause_chunk

pdf_path = Path("data/contracts/sample.pdf")

docs = load_pdf(pdf_path)
cleaned_docs = [clean_text(d) for d in docs]

all_chunks = []
for doc in cleaned_docs:
    chunks = clause_chunk(doc)
    all_chunks.extend(chunks)

print(all_chunks[:2])
print(f"Total chunks created: {len(all_chunks)}")
