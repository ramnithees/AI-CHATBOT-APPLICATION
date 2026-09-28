from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME


class AIChatbot:

    def __init__(self):

        self.client = Groq(
            api_key=GROQ_API_KEY
        )

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly and helpful AI assistant. "
                    "Answer clearly and accurately."
                )
            }
        ]


    # ========================================================
    # NORMAL CHAT / DOCUMENT CHAT
    # ========================================================

    def ask(
        self,
        prompt,
        temperature=0.7,
        max_tokens=1024,
        document_text=None,
        document_name=None
    ):

        # ----------------------------------------------------
        # NORMAL CHAT
        # ----------------------------------------------------

        if not document_text:

            user_content = prompt


        # ----------------------------------------------------
        # DOCUMENT CHAT
        # ----------------------------------------------------

        else:

            user_content = f"""
The user has uploaded a document.

Document name:
{document_name or "Uploaded document"}

DOCUMENT CONTENT:
-------------------------
{document_text}
-------------------------

USER QUESTION:
{prompt}

INSTRUCTIONS:
Use the uploaded document when answering questions about it.

If the answer is present in the document, answer using the
document content.

If the requested information is not contained in the document,
say that it is not found in the uploaded document.

You may provide general knowledge only when it is useful, but
clearly identify it as additional information rather than
information from the document.

Do not invent information or claim that something appears in
the document when it does not.
"""


        # ----------------------------------------------------
        # ADD MESSAGE TO AI MEMORY
        # ----------------------------------------------------

        self.messages.append(
            {
                "role": "user",
                "content": user_content
            }
        )


        # ----------------------------------------------------
        # SEND REQUEST TO GROQ
        # ----------------------------------------------------

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.messages,
            temperature=temperature,
            max_tokens=max_tokens
        )


        reply = (
            response
            .choices[0]
            .message
            .content
        )


        # ----------------------------------------------------
        # ADD RESPONSE TO AI MEMORY
        # ----------------------------------------------------

        self.messages.append(
            {
                "role": "assistant",
                "content": reply
            }
        )


        return reply


    # ========================================================
    # CLEAR CHATBOT MEMORY
    # ========================================================

    def clear(self):

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly and helpful AI assistant. "
                    "Answer clearly and accurately."
                )
            }
        ]