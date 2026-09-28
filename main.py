from chatbot import AIChatbot
from history import ChatHistory
import ui
import time

bot = AIChatbot()
history = ChatHistory()

message_count = 0

ui.banner()

while True:

    user = input(ui.user())

    if user.lower() == "exit":
        print("👋 Goodbye!")
        break

    if user == "/help":
        print("""
Available Commands
------------------
/help      Show commands
/stats     Chat statistics
/clear     Clear terminal
exit       Quit
""")
        continue

    if user == "/stats":
        print(f"\nMessages Sent : {message_count}")
        continue

    if user == "/clear":
        import os
        os.system("cls")
        ui.banner()
        continue

    history.save("User", user)

    start = time.time()

    try:

        reply = bot.ask(user)

        elapsed = time.time() - start

        ui.ai(reply)

        print(f"\n⏱ Response Time : {elapsed:.2f} sec")

        history.save("AI", reply)

        message_count += 1

    except Exception as e:

        ui.error(e)