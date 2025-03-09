import xmlrpc.client

s = xmlrpc.client.ServerProxy("http://localhost:8000/RPC2")

def add_note():
    topic = input("Enter the topic: ")
    text = input("Enter your note: ")
    response = s.add_entry(topic, text)
    print(response)

def receive_notes():
    topic = input("Enter the topic to retrieve notes from: ")
    entries = s.retrieve_entries(topic)
    if entries:
        print(f"\nEntries for topic '{topic}':")
        for timestamp, text in entries:
            print(f"[{timestamp} {text}]")
    else:
        print(f"No entries found for topic '{topic}'.")

def search_wikipedia():
    query = input("What do you want to know about?: ")
    result = s.wiki_search({"query": query})

    if "summary" in result:
        print(f"\nWikipedia Summary: {result['summary']}")
        print(f"Full article: {result['link']}")

        choice = input("\nDo you want to append this to a topic? (yes/no): ").strip().lower()
        if choice == "yes":
            topic = input("Enter topic to append Wikipedia summary: ")
            append_result = s.wiki_search({"query": query, "append": True, "topic": topic})
            print(f"Data has been appended to topic '{topic}'")

    else:
        print(result)

while True:
    print("\nNotebook Client")
    print("1. Add a note")
    print("2. Retrieve notes")
    print("3. Search from Wikipedia")
    print("4. Exit")
    choice = input("Choose a option: ")

    if choice == "1":
        add_note()
    elif choice == "2":
        receive_notes()
    elif choice == "3":
        search_wikipedia()
    elif choice == "4":
        print("Exiting notebook application...")
        break
    else:
        print("Invalid choice, please try again 1-3.")