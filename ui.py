from colorama import Fore, Style, init
import time

init(autoreset=True)


def banner():
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + "        🤖 GROQ AI CHATBOT")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "Type /help for commands")
    print()


def user():
    return Fore.BLUE + "You: " + Style.RESET_ALL


def ai(text):
    print(Fore.GREEN + "\nAI: ", end="")
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(0.01)
    print()


def error(msg):
    print(Fore.RED + f"\nError: {msg}")