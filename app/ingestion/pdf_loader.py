from pathlib import Path
import pdfplumber
from typing import List, Dict

from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_pdf(file_path: Path) -> List[Dict]:
    """
    Extract text from a PDF file page by page.

    Returns:
        List of dicts with:
        - text
        - page_number
        - source_file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    documents = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()

            if not text:
                logger.warning(f"No text found on page {page_number}")
                continue

            documents.append({
                "text": text,
                "page_number": page_number,
                "source_file": file_path.name
            })

    logger.info(f"Loaded {len(documents)} pages from {file_path.name}")
    return documents
