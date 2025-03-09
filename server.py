import xml.etree.ElementTree as ET
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import datetime
import threading
import requests

DB_FILE = "data.xml"

# Checking the existance of the Database
def initialize_db():
    try:
        tree = ET.parse(DB_FILE)
        return tree
    except FileNotFoundError:
        root = ET.Element("data")
        tree = ET.ElementTree(root)
        tree.write(DB_FILE)
        return

# Use thread locks to prevent data corruption
lock = threading.Lock()

def add_entry(topic, text):
    with lock:
        tree = initialize_db()
        root = tree.getroot()

        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        #Checking if topic exists and adding the entry if topic is found
        for t in root.findall("topic"):
            if t.get("name") == topic:
                new_entry = ET.Element("entry", timestamp=timestamp)
                new_entry.text = text
                t.append(new_entry)
                tree.write(DB_FILE)
                return f"Added new entry to topic '{topic}'."
        
        #If topic doesn't exist, add it
        new_topic = ET.Element("topic", name=topic)
        new_entry = ET.Element("entry", timestamp=timestamp)
        new_entry.text = text
        new_topic.append(new_entry)
        root.append(new_topic)
        tree.write(DB_FILE)
        return f"Created new topic '{topic}' and added entry."
    
def retrieve_entries(topic):
    with lock:
        tree = initialize_db()
        root = tree.getroot()

        for t in root.findall("topic"):
            if t.get("name") == topic:
                return [(e.get("timestamp"), e.text) for e in t.findall("entry")]
        
        return["Topic not found."] #topic not found

def wiki_search(args):
    query = args["query"]
    append = args.get("append", False)
    topic = args.get("topic", None)

    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": query
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Error fetching Wikipedia data (status {response.status_code})."
    
    data = response.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    if "extract" not in page:
        return f"No Wikipedia article found for '{query}'."
    
    summary = page["extract"]
    link = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"

    if append and topic:
        add_entry(topic, f"Wikipedia: {summary}")

    return {"summary": summary, "link": link}



#Threaded XML-RPC server should handle multiple clients
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)

with ThreadedXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler) as server:
    server.register_function(add_entry, "add_entry")
    server.register_function(retrieve_entries, "retrieve_entries")
    server.register_function(wiki_search, "wiki_search")

    print("Server is Running on port 8000...")

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("Shutting down server...")
            server.shutdown()
            break
