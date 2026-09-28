import re


# ============================================================
# SPLIT DOCUMENT INTO CHUNKS
# ============================================================

def split_document(
    text,
    chunk_size=1500,
    overlap=200
):

    if not text:
        return []

    text = text.strip()

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end]

        # Try to finish the chunk at a natural boundary
        if end < text_length:

            last_newline = chunk.rfind("\n")
            last_period = chunk.rfind(".")

            boundary = max(
                last_newline,
                last_period
            )

            # Don't make the chunk too small
            if boundary > chunk_size // 2:
                chunk = chunk[:boundary + 1]
                end = start + boundary + 1

        chunk = chunk.strip()

        if chunk:
            chunks.append(chunk)

        # Move forward while keeping some overlap
        next_start = end - overlap

        # Safety check
        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


# ============================================================
# NORMALIZE WORDS
# ============================================================

def get_words(text):

    return set(
        re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )
    )


# ============================================================
# SCORE CHUNK
# ============================================================

def score_chunk(chunk, question):

    question_words = get_words(question)

    chunk_words = get_words(chunk)

    if not question_words:
        return 0

    common_words = (
        question_words.intersection(
            chunk_words
        )
    )

    return len(common_words)


# ============================================================
# FIND RELEVANT CHUNKS
# ============================================================

def find_relevant_chunks(
    question,
    chunks,
    top_k=3
):

    if not chunks:
        return []

    scored_chunks = []

    for index, chunk in enumerate(chunks):

        score = score_chunk(
            chunk,
            question
        )

        scored_chunks.append(
            (
                score,
                index,
                chunk
            )
        )

    # Highest score first
    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # Keep chunks that actually matched the question
    relevant = [
        item
        for item in scored_chunks
        if item[0] > 0
    ]

    # If no keyword match exists,
    # provide the first chunks as fallback.
    if not relevant:

        relevant = scored_chunks[:top_k]

    else:

        relevant = relevant[:top_k]

    return [
        {
            "chunk_number": index + 1,
            "score": score,
            "text": chunk
        }
        for score, index, chunk in relevant
    ]


# ============================================================
# BUILD DOCUMENT CONTEXT
# ============================================================

def build_document_context(
    question,
    chunks,
    top_k=3
):

    relevant_chunks = find_relevant_chunks(
        question,
        chunks,
        top_k
    )

    context_parts = []

    for item in relevant_chunks:

        context_parts.append(
            f"""
--- Document Chunk {item['chunk_number']} ---

{item['text']}
"""
        )

    return "\n".join(context_parts)