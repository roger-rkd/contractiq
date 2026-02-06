import re
from typing import Dict

from app.utils.logger import get_logger

logger = get_logger(__name__)


def clean_text(document: Dict) -> Dict:
    """
    Clean extracted text while preserving legal meaning.
    """
    text = document["text"]

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove common footer/header artifacts
    text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)

    cleaned_doc = {
        **document,
        "text": text.strip()
    }

    logger.debug(
        f"Cleaned text for page {document['page_number']} "
        f"({document['source_file']})"
    )

    return cleaned_doc
