import sqlite3

conn = sqlite3.connect("database/chatbot.db")
cursor = conn.cursor()

print("========== CHATS ==========")

cursor.execute("SELECT * FROM chats")
for row in cursor.fetchall():
    print(row)

print("\n========== MESSAGES ==========")

cursor.execute("SELECT * FROM messages")
for row in cursor.fetchall():
    print(row)

conn.close()