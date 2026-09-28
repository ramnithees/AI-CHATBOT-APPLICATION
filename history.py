from pathlib import Path
from datetime import datetime


class ChatHistory:

    def __init__(self):
        folder = Path("chat_history")
        folder.mkdir(exist_ok=True)

        filename = datetime.now().strftime("chat_%Y-%m-%d_%H-%M-%S.txt")
        self.file = folder / filename

        with open(self.file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("Groq AI Chatbot Conversation\n")
            f.write("=" * 60 + "\n\n")

    def save(self, speaker, message):

        time = datetime.now().strftime("%H:%M:%S")

        with open(self.file, "a", encoding="utf-8") as f:
            f.write(f"[{time}] {speaker}: {message}\n\n")