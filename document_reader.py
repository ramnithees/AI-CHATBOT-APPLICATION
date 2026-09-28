import fitz


# ============================================================
# READ TXT FILE
# ============================================================

def read_txt_file(uploaded_file):

    try:
        uploaded_file.seek(0)

        text = uploaded_file.read().decode(
            "utf-8",
            errors="replace"
        )

        uploaded_file.seek(0)

        return text

    except Exception as e:

        raise Exception(
            f"Could not read TXT file: {e}"
        )


# ============================================================
# READ PDF FILE
# ============================================================

def read_pdf_file(uploaded_file):

    try:
        uploaded_file.seek(0)

        pdf_bytes = uploaded_file.read()

        uploaded_file.seek(0)

        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        pages = []

        for page_number, page in enumerate(
            document,
            start=1
        ):

            page_text = page.get_text("text")

            pages.append(
                f"\n--- Page {page_number} ---\n"
                f"{page_text}"
            )

        document.close()

        return "\n".join(pages)

    except Exception as e:

        raise Exception(
            f"Could not read PDF file: {e}"
        )


# ============================================================
# EXTRACT DOCUMENT TEXT
# ============================================================

def extract_document_text(uploaded_file):

    if uploaded_file is None:

        return ""


    file_name = uploaded_file.name.lower()


    if file_name.endswith(".pdf"):

        return read_pdf_file(
            uploaded_file
        )


    elif file_name.endswith(".txt"):

        return read_txt_file(
            uploaded_file
        )


    else:

        raise ValueError(
            "Unsupported file type. "
            "Please upload a PDF or TXT file."
        )