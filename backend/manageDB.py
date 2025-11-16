import chromadb

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Get all collections
collections = client.list_collections()

# Delete all collections if they exist
if collections:
    for collection in collections:
        client.delete_collection(collection.name)
    print("Reset DB")
else:
    print("No existing DB.")
