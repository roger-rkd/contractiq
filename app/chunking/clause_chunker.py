"""
Enhanced clause chunking with sub-clause level granularity and semantic enrichment.
"""
import re
from typing import List, Dict, Tuple
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Enhanced clause intent mapping with more variations
CLAUSE_KEYWORDS = {
    "GOVERNING LAW": [
        "governing law", "law", "jurisdiction", "legal framework",
        "applicable law", "law of", "courts of"
    ],
    "TERMINATION": [
        "termination", "terminate", "end this agreement", "cancellation",
        "cancel", "cease", "discontinue", "expiry", "expire"
    ],
    "DATA PROTECTION": [
        "data protection", "personal data", "privacy", "gdpr",
        "data subject", "data processing", "confidential information",
        "sensitive data", "information security"
    ],
    "CONFIDENTIALITY": [
        "confidential", "confidentiality", "non-disclosure",
        "proprietary", "secret", "classified"
    ],
    "LIABILITY": [
        "liability", "liable", "damages", "indemnity", "indemnification",
        "responsibility", "fault", "negligence", "loss"
    ],
    "PAYMENT": [
        "payment", "fees", "charges", "invoice", "cost",
        "price", "billing", "remuneration", "compensation"
    ],
    "INTELLECTUAL PROPERTY": [
        "intellectual property", "ip", "ownership", "copyright",
        "trademark", "patent", "proprietary rights"
    ],
    "WARRANTY": [
        "warranty", "guarantee", "assurance", "representation",
        "warranted", "guaranteed"
    ],
    "DISPUTE RESOLUTION": [
        "dispute", "arbitration", "mediation", "resolution",
        "conflict", "disagreement"
    ],
    "FORCE MAJEURE": [
        "force majeure", "act of god", "unforeseen circumstances",
        "beyond control"
    ]
}


def detect_clause_title(line: str) -> Tuple[str | None, str | None]:
    """
    Detect whether a line is a clause/sub-clause heading.

    Returns:
        Tuple of (clause_title, clause_number)
        e.g., ("TERMINATION", "10.2") or (None, None)
    """
    clean = line.strip().upper()

    # Pattern 1: Numbered headings with title
    # Matches: "10 TERMINATION", "10.2 TERMINATION CONDITIONS", "10.2.1 Breach"
    match = re.match(r"^(\d+(?:\.\d+)*)\s+(.+)", clean)
    if match:
        clause_number = match.group(1)
        heading = match.group(2).strip()

        # Check if heading matches any known clause type
        for title, keywords in CLAUSE_KEYWORDS.items():
            if any(keyword.upper() in heading for keyword in keywords):
                return title, clause_number

        # If no match, use the heading itself as the title
        return heading[:50], clause_number  # Limit title length

    # Pattern 2: Just a title (no number)
    for title, keywords in CLAUSE_KEYWORDS.items():
        if any(keyword.upper() in clean for keyword in keywords):
            return title, None

    return None, None


def extract_semantic_keywords(text: str, clause_title: str) -> List[str]:
    """
    Extract semantic keywords from text for enrichment.

    Args:
        text: The clause text
        clause_title: The title of the clause

    Returns:
        List of semantic keywords found in the text
    """
    keywords = []

    # Get keywords for this clause type
    if clause_title in CLAUSE_KEYWORDS:
        for keyword in CLAUSE_KEYWORDS[clause_title]:
            if keyword.lower() in text.lower():
                keywords.append(keyword)

    return keywords


def split_into_subclauses(text: str) -> List[str]:
    """
    Split text into sub-clauses for finer granularity.

    Splits on:
    - Numbered sub-clauses (e.g., "10.2.1", "(a)", "(i)")
    - Bullet points or list items
    - Sentence boundaries (if text is very long)

    Args:
        text: The clause text to split

    Returns:
        List of sub-clause texts
    """
    subclauses = []

    # Pattern 1: Split on numbered sub-clauses like "10.2.1" or "(a)" or "(i)"
    # This regex looks for patterns like:
    # - "10.2.1" or "10.2.1."
    # - "(a)" or "(i)"
    # - "a)" or "i)"
    subclause_pattern = r'(?:^|\n)\s*(?:(?:\d+\.)+\d+\.?\s+|\([a-z0-9]+\)\s+|[a-z0-9]\)\s+)'

    parts = re.split(subclause_pattern, text, flags=re.MULTILINE)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # If part is very long (>500 chars), split on sentence boundaries
        if len(part) > 500:
            sentences = re.split(r'(?<=[.!?])\s+', part)
            current_chunk = ""

            for sentence in sentences:
                if len(current_chunk) + len(sentence) < 500:
                    current_chunk += sentence + " "
                else:
                    if current_chunk.strip():
                        subclauses.append(current_chunk.strip())
                    current_chunk = sentence + " "

            if current_chunk.strip():
                subclauses.append(current_chunk.strip())
        else:
            subclauses.append(part)

    # If no subclauses were found, return the original text
    if not subclauses:
        subclauses = [text]

    return subclauses


def enrich_text_with_semantics(
    text: str,
    clause_title: str,
    clause_number: str | None,
    keywords: List[str]
) -> str:
    """
    Enrich text with semantic metadata for better retrieval.

    Adds:
    - Clause type/title
    - Clause number (if available)
    - Relevant keywords
    - Semantic context

    Args:
        text: The original clause text
        clause_title: The title of the clause
        clause_number: The number of the clause (e.g., "10.2")
        keywords: Semantic keywords found in the text

    Returns:
        Enriched text optimized for embedding
    """
    enrichment_parts = []

    # Part 1: Clause type
    enrichment_parts.append(f"[{clause_title}]")

    # Part 2: Clause number (if available)
    if clause_number:
        enrichment_parts.append(f"Clause {clause_number}:")

    # Part 3: Keywords (if any)
    if keywords:
        keyword_str = ", ".join(keywords[:5])  # Limit to 5 keywords
        enrichment_parts.append(f"Keywords: {keyword_str}.")

    # Part 4: Original text
    enrichment_parts.append(text)

    # Combine all parts
    enriched = " ".join(enrichment_parts)

    return enriched


def clause_chunk(document: Dict) -> List[Dict]:
    """
    Split a contract page into semantically enriched sub-clause chunks.

    Improvements over previous version:
    1. Sub-clause level chunking for finer granularity
    2. Enhanced semantic enrichment with keywords
    3. Clause number extraction and inclusion
    4. Better text splitting logic

    Args:
        document: Dict with 'text', 'page_number', 'source_file'

    Returns:
        List of enriched chunk dicts
    """
    text = document["text"]
    page_number = document["page_number"]
    source_file = document["source_file"]

    # Split text into lines
    lines = text.split('\n')

    chunks = []
    current_clause = {
        "clause_title": "GENERAL",
        "clause_number": None,
        "text": "",
        "page_number": page_number,
        "source_file": source_file
    }

    # Process each line
    for line in lines:
        detected_title, detected_number = detect_clause_title(line)

        if detected_title:
            # Save the previous clause if it has content
            if current_clause["text"].strip():
                chunks.append(current_clause.copy())

            # Start a new clause
            current_clause = {
                "clause_title": detected_title,
                "clause_number": detected_number,
                "text": "",
                "page_number": page_number,
                "source_file": source_file
            }
        else:
            # Add line to current clause
            current_clause["text"] += line + " "

    # Don't forget the last clause
    if current_clause["text"].strip():
        chunks.append(current_clause)

    # If no clauses were detected, treat entire page as one chunk
    if not chunks:
        chunks.append({
            "clause_title": "GENERAL",
            "clause_number": None,
            "text": text,
            "page_number": page_number,
            "source_file": source_file
        })

    # Process chunks: split into subclauses and enrich
    enriched_chunks = []

    for chunk in chunks:
        clause_title = chunk["clause_title"]
        clause_number = chunk["clause_number"]
        clause_text = chunk["text"].strip()

        if not clause_text:
            continue

        # Extract semantic keywords
        keywords = extract_semantic_keywords(clause_text, clause_title)

        # Split into sub-clauses for finer granularity
        subclauses = split_into_subclauses(clause_text)

        # Create enriched chunk for each sub-clause
        for i, subclause_text in enumerate(subclauses):
            if not subclause_text.strip():
                continue

            # Create sub-clause number (e.g., "10.2.1")
            subclause_number = clause_number
            if clause_number and len(subclauses) > 1:
                subclause_number = f"{clause_number}.{i+1}"

            # Enrich the text
            enriched_text = enrich_text_with_semantics(
                subclause_text,
                clause_title,
                subclause_number,
                keywords
            )

            enriched_chunks.append({
                "clause_title": clause_title,
                "text": enriched_text,
                "page_number": page_number,
                "source_file": source_file
            })

    logger.info(
        f"Created {len(enriched_chunks)} enriched sub-clause chunks "
        f"from page {page_number} ({len(chunks)} main clauses)"
    )

    return enriched_chunks
