import streamlit as st
import time

from chatbot import AIChatbot

from database import (
    initialize_database,
    create_chat,
    save_message,
    get_all_chats,
    get_messages,
    update_chat_title,
    delete_chat,
    clear_chat_messages
)

from document_reader import extract_document_text

from document_processor import (
    split_document,
    find_relevant_chunks,
    build_document_context
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Groq AI Chatbot",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# RENAME CHAT DIALOG
# ============================================================

@st.dialog("✏️ Rename Chat")
def rename_chat_dialog(chat_id, current_title):

    new_title = st.text_input(
        "Chat name",
        value=current_title
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Save",
            use_container_width=True
        ):

            new_title = new_title.strip()

            if new_title:

                update_chat_title(
                    chat_id,
                    new_title
                )

                st.rerun()

            else:

                st.warning(
                    "Chat name cannot be empty."
                )

    with col2:

        if st.button(
            "❌ Cancel",
            use_container_width=True
        ):

            st.rerun()


# ============================================================
# DELETE CHAT DIALOG
# ============================================================

@st.dialog("⚠️ Delete Chat")
def delete_chat_dialog(chat_id, chat_title):

    st.warning(
        f"Are you sure you want to delete **{chat_title}**?"
    )

    st.write(
        "This will permanently delete the chat "
        "and all its messages."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🗑️ Delete",
            use_container_width=True
        ):

            delete_chat(chat_id)

            if st.session_state.chat_id == chat_id:

                new_chat_id = create_chat(
                    "New Chat"
                )

                st.session_state.chat_id = new_chat_id

                st.session_state.messages = []

                st.session_state.bot.clear()

                st.session_state.uploaded_file_name = None
                st.session_state.document_text = ""
                st.session_state.document_chunks = []
                st.session_state.processed_file_name = None

            st.rerun()

    with col2:

        if st.button(
            "❌ Cancel",
            use_container_width=True
        ):

            st.rerun()


# ============================================================
# CLEAR CHAT DIALOG
# ============================================================

@st.dialog("🧹 Clear Conversation")
def clear_chat_dialog():

    st.warning(
        "Are you sure you want to clear this conversation?"
    )

    st.write(
        "All messages in the current chat will be permanently "
        "deleted. The chat itself will remain."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🧹 Clear Messages",
            use_container_width=True
        ):

            clear_chat_messages(
                st.session_state.chat_id
            )

            st.session_state.messages = []

            st.session_state.bot.clear()

            st.rerun()

    with col2:

        if st.button(
            "❌ Cancel",
            use_container_width=True
        ):

            st.rerun()


# ============================================================
# SESSION STATE
# ============================================================

if "bot" not in st.session_state:
    st.session_state.bot = AIChatbot()


if "messages" not in st.session_state:
    st.session_state.messages = []


if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


if "document_text" not in st.session_state:
    st.session_state.document_text = ""


# NEW:
# Stores chunks generated from the uploaded document
if "document_chunks" not in st.session_state:
    st.session_state.document_chunks = []


if "processed_file_name" not in st.session_state:
    st.session_state.processed_file_name = None


if "chat_id" not in st.session_state:

    chats = get_all_chats()

    if chats:

        st.session_state.chat_id = chats[0][0]

        saved_messages = get_messages(
            st.session_state.chat_id
        )

        st.session_state.messages = []

        for role, message in saved_messages:

            st.session_state.messages.append(
                {
                    "role": role,
                    "content": message
                }
            )

        st.session_state.bot.clear()

        for role, message in saved_messages:

            st.session_state.bot.messages.append(
                {
                    "role": role,
                    "content": message
                }
            )

    else:

        st.session_state.chat_id = create_chat(
            "New Chat"
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 Groq AI Chatbot")


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "🆕 New Chat",
        use_container_width=True
    ):

        new_chat_id = create_chat(
            "New Chat"
        )

        st.session_state.chat_id = new_chat_id

        st.session_state.messages = []

        st.session_state.bot.clear()

        st.session_state.uploaded_file_name = None
        st.session_state.document_text = ""
        st.session_state.document_chunks = []
        st.session_state.processed_file_name = None

        st.rerun()


    # ========================================================
    # CLEAR CURRENT CHAT
    # ========================================================

    if st.button(
        "🧹 Clear Current Chat",
        use_container_width=True
    ):

        clear_chat_dialog()


    st.divider()


    # ========================================================
    # DOCUMENT UPLOAD
    # ========================================================

    st.subheader("📄 Documents")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt"],
        help="Supported file types: PDF and TXT"
    )


    # ========================================================
    # PROCESS DOCUMENT
    # ========================================================

    if uploaded_file is not None:

        st.session_state.uploaded_file_name = (
            uploaded_file.name
        )

        file_size = uploaded_file.size


        # ----------------------------------------------------
        # FILE SIZE
        # ----------------------------------------------------

        if file_size < 1024 * 1024:

            size_text = (
                f"{file_size / 1024:.2f} KB"
            )

        else:

            size_text = (
                f"{file_size / (1024 * 1024):.2f} MB"
            )


        # ----------------------------------------------------
        # EXTRACT + CHUNK DOCUMENT
        # ----------------------------------------------------

        if (
            st.session_state.processed_file_name
            != uploaded_file.name
        ):

            try:

                with st.spinner(
                    "📖 Processing document..."
                ):

                    # Extract text from PDF/TXT
                    extracted_text = (
                        extract_document_text(
                            uploaded_file
                        )
                    )

                    # Store full extracted text
                    st.session_state.document_text = (
                        extracted_text
                    )

                    # Split document into chunks
                    st.session_state.document_chunks = (
                        split_document(
                            extracted_text,
                            chunk_size=1500,
                            overlap=200
                        )
                    )

                    st.session_state.processed_file_name = (
                        uploaded_file.name
                    )

            except Exception as e:

                st.session_state.document_text = ""

                st.session_state.document_chunks = []

                st.session_state.processed_file_name = None

                st.error(
                    f"❌ Document processing failed: {e}"
                )


        # ----------------------------------------------------
        # DOCUMENT INFORMATION
        # ----------------------------------------------------

        st.write(
            f"**File:** {uploaded_file.name}"
        )

        st.write(
            f"**Size:** {size_text}"
        )


        if st.session_state.document_text.strip():

            st.success(
                "✅ Document processed successfully!"
            )

            word_count = len(
                st.session_state.document_text.split()
            )

            character_count = len(
                st.session_state.document_text
            )

            chunk_count = len(
                st.session_state.document_chunks
            )

            st.write(
                f"**Words extracted:** "
                f"{word_count:,}"
            )

            st.write(
                f"**Characters extracted:** "
                f"{character_count:,}"
            )

            st.write(
                f"**Document chunks:** "
                f"{chunk_count}"
            )

            st.info(
                "🧠 RAG mode is active.\n\n"
                "The chatbot will retrieve relevant "
                "sections of the document."
            )

        else:

            st.warning(
                "⚠️ No readable text was found "
                "in this document."
            )


    st.divider()


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    st.subheader("💬 Chat History")

    chats = get_all_chats()


    for chat_id, title in chats:

        if not title:
            title = "New Chat"


        col1, col2, col3 = st.columns(
            [5, 1, 1]
        )


        # ====================================================
        # OPEN CHAT
        # ====================================================

        with col1:

            if st.button(
                f"💬 {title}",
                key=f"chat_{chat_id}",
                use_container_width=True
            ):

                st.session_state.chat_id = chat_id

                st.session_state.messages = []

                saved_messages = get_messages(
                    chat_id
                )


                for role, message in saved_messages:

                    st.session_state.messages.append(
                        {
                            "role": role,
                            "content": message
                        }
                    )


                st.session_state.bot.clear()


                for role, message in saved_messages:

                    st.session_state.bot.messages.append(
                        {
                            "role": role,
                            "content": message
                        }
                    )


                # Document attachment is temporary
                st.session_state.uploaded_file_name = None
                st.session_state.document_text = ""
                st.session_state.document_chunks = []
                st.session_state.processed_file_name = None

                st.rerun()


        # ====================================================
        # RENAME CHAT
        # ====================================================

        with col2:

            if st.button(
                "✏️",
                key=f"rename_{chat_id}",
                help="Rename this chat"
            ):

                rename_chat_dialog(
                    chat_id,
                    title
                )


        # ====================================================
        # DELETE CHAT
        # ====================================================

        with col3:

            if st.button(
                "🗑️",
                key=f"delete_{chat_id}",
                help="Delete this chat"
            ):

                delete_chat_dialog(
                    chat_id,
                    title
                )


    st.divider()


    # ========================================================
    # SETTINGS
    # ========================================================

    st.subheader("⚙️ Settings")


    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )


    max_tokens = st.slider(
        "Max Tokens",
        min_value=100,
        max_value=4096,
        value=1024,
        step=100
    )


    st.divider()


    st.info(
        "Groq AI Chatbot\n\n"
        "Built with Python + Streamlit"
    )


# ============================================================
# MAIN CHAT AREA
# ============================================================

st.title("🤖 Groq AI Chatbot")

st.caption(
    "Powered by Groq + OpenAI GPT-OSS 120B"
)


# ============================================================
# DOCUMENT STATUS
# ============================================================

if (
    st.session_state.uploaded_file_name
    and st.session_state.document_chunks
):

    st.success(
        f"📎 Document ready: "
        f"{st.session_state.uploaded_file_name}"
    )

    st.caption(
        f"🧠 RAG active • "
        f"{len(st.session_state.document_chunks)} chunks"
    )


# ============================================================
# DISPLAY MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Ask anything..."
)


if prompt:

    # ========================================================
    # CHECK EXISTING MESSAGES
    # ========================================================

    existing_messages = get_messages(
        st.session_state.chat_id
    )


    # ========================================================
    # AUTOMATIC CHAT TITLE
    # ========================================================

    if len(existing_messages) == 0:

        title = prompt.strip()

        if len(title) > 40:

            title = (
                title[:40] + "..."
            )

        update_chat_title(
            st.session_state.chat_id,
            title
        )


    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    with st.chat_message("user"):

        st.markdown(prompt)


    save_message(
        st.session_state.chat_id,
        "user",
        prompt
    )


    # ========================================================
    # GENERATE AI RESPONSE
    # ========================================================

    start = time.time()


    try:

        # ====================================================
        # RAG DOCUMENT MODE
        # ====================================================

        if st.session_state.document_chunks:

            # Find the most relevant document sections
            relevant_chunks = (
                find_relevant_chunks(
                    question=prompt,
                    chunks=(
                        st.session_state.document_chunks
                    ),
                    top_k=3
                )
            )


            # Build smaller context for Groq
            document_context = (
                build_document_context(
                    question=prompt,
                    chunks=(
                        st.session_state.document_chunks
                    ),
                    top_k=3
                )
            )


            # Send only relevant context,
            # NOT the whole document.
            reply = st.session_state.bot.ask(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                document_text=document_context,
                document_name=(
                    st.session_state.uploaded_file_name
                )
            )


        # ====================================================
        # NORMAL CHAT MODE
        # ====================================================

        else:

            reply = st.session_state.bot.ask(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )


    except Exception as e:

        reply = f"❌ Error: {e}"


    elapsed = time.time() - start


    # ========================================================
    # DISPLAY AI RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        st.markdown(reply)

        st.caption(
            f"⚡ Response Time: "
            f"{elapsed:.2f} seconds"
        )


    # ========================================================
    # SAVE AI RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )


    save_message(
        st.session_state.chat_id,
        "assistant",
        reply
    )