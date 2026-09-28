from document_processor import (
    split_document,
    find_relevant_chunks
)


sample_text = """
Python is a popular programming language.
It is commonly used for automation and data science.

Machine learning allows computers to learn patterns from data.
Machine learning is widely used in artificial intelligence.

SQLite is a lightweight relational database.
It stores information in database files.

Streamlit is a Python framework used to create web applications.
It is especially useful for data and AI applications.
"""


chunks = split_document(
    sample_text,
    chunk_size=150,
    overlap=30
)


print("=" * 50)
print("DOCUMENT CHUNKS")
print("=" * 50)


for number, chunk in enumerate(
    chunks,
    start=1
):

    print(
        f"\nCHUNK {number}"
    )

    print(chunk)


question = (
    "What does the document say "
    "about machine learning?"
)


results = find_relevant_chunks(
    question,
    chunks,
    top_k=2
)


print("\n")
print("=" * 50)
print("RELEVANT CHUNKS")
print("=" * 50)


for result in results:

    print(
        f"\nChunk: "
        f"{result['chunk_number']}"
    )

    print(
        f"Score: "
        f"{result['score']}"
    )

    print(
        result["text"]
    )