from nltk.chat.util import Chat, reflections

pairs = [
    ["hi", ["Hello!"]],
    ["hello", ["Hi there!"]],
    ["how are you", ["I'm good! How about you?"]],
    ["your name", ["I'm ChatBot, your assistant!"]],
    ["bye", ["Goodbye! 👋"]],
]

chat = Chat(pairs, reflections)
print("ChatBot: Hello! Type 'quit' to exit.\n")

while True:
    user = input("You: ").lower()
    if user == "quit":
        print("ChatBot: Bye! 👋")
        break

    reply = chat.respond(user)
    if reply:
        print("ChatBot:", reply)
    else:
        print("ChatBot: I don't know that yet 🤔")
        ans = input("Teach me what to reply: ")
        pairs.append([user, [ans]])
        chat = Chat(pairs, reflections)
        print("ChatBot: Got it! I'll remember that ✅")
