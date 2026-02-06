"""
Prompt templates for RAG system with citation-first enforcement.
"""


def build_citation_first_prompt(question: str, contexts: list[dict]) -> list[dict]:
    """
    Build a STRICT citation-first prompt that enforces:
    1. Every answer MUST start with a citation
    2. No answer without explicit source reference
    3. Hard refusal when information is not found
    """

    # Build numbered context blocks with clear references
    context_blocks = []
    for i, ctx in enumerate(contexts, start=1):
        clause_title = ctx["metadata"].get("clause_title", "Unknown Clause")
        page = ctx["metadata"].get("page_number", "N/A")
        text = ctx.get("text", "")

        block = (
            f"[Clause {i}]\n"
            f"Title: {clause_title}\n"
            f"Page: {page}\n"
            f"Content: {text}\n"
        )
        context_blocks.append(block)

    context_text = "\n".join(context_blocks)

    system_prompt = (
        "You are a legal contract analysis assistant with STRICT citation requirements.\n\n"

        "CRITICAL RULES (VIOLATION = FAILURE):\n\n"

        "1. CITATION-FIRST REQUIREMENT:\n"
        "   - Every answer MUST begin with \"According to [Clause X]...\" or \"Based on [Clause X]...\"\n"
        "   - You MUST reference the specific clause number [Clause 1], [Clause 2], etc.\n"
        "   - NEVER provide information without citing the exact clause\n\n"

        "2. GROUNDING REQUIREMENT:\n"
        "   - ONLY use information explicitly stated in the provided clauses\n"
        "   - Do NOT paraphrase beyond what is directly stated\n"
        "   - Do NOT use external legal knowledge\n"
        "   - Do NOT make inferences or assumptions\n\n"

        "3. REFUSAL REQUIREMENT:\n"
        "   - If the answer is NOT found in any clause, you MUST respond EXACTLY:\n"
        "     \"INSUFFICIENT_INFORMATION: The contract does not specify this.\"\n"
        "   - Do NOT attempt to answer if information is missing\n"
        "   - Do NOT use phrases like 'likely', 'probably', 'typically'\n\n"

        "4. FORMAT REQUIREMENT:\n"
        "   - Start with citation: \"According to [Clause X], ...\"\n"
        "   - State the facts from that clause\n"
        "   - If multiple clauses: cite each one separately\n"
        "   - End with a summary if needed\n\n"

        "EXAMPLES:\n\n"

        "Good answer:\n"
        "\"According to [Clause 2], the termination notice period is 30 days. "
        "Based on [Clause 3], termination can occur if payment is not received within this period.\"\n\n"

        "Bad answer (NEVER do this):\n"
        "\"The termination period is typically 30 days.\" ❌ (No citation)\n"
        "\"Based on standard practice, ...\" ❌ (External knowledge)\n"
        "\"The contract likely states...\" ❌ (Speculation)\n\n"

        "REMEMBER: Citation first, then facts. No citation = refuse to answer."
    )

    user_prompt = (
        "CONTRACT CLAUSES:\n\n"
        f"{context_text}\n\n"
        "---\n\n"
        f"QUESTION: {question}\n\n"
        "INSTRUCTIONS:\n"
        "- If the answer exists in the clauses above, provide it with citations\n"
        "- Start your answer with \"According to [Clause X]...\"\n"
        "- If the answer does NOT exist, respond: \"INSUFFICIENT_INFORMATION: The contract does not specify this.\"\n\n"
        "ANSWER:"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
