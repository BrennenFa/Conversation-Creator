import json
import argparse
from sentence_transformers import SentenceTransformer
import chromadb

# Command line Chroma DB arguements
parser = argparse.ArgumentParser(description='Initialize or update Chroma DB')
parser.add_argument('--clear', action='store_true', help='Clear existing data before loading')
args = parser.parse_args()

# Load trends.json
with open('Trends/trends.json', 'r') as f:
    data = json.load(f)

# intialize embeddings, chromaDB
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")

# Handle clear flag (reseting database)
if args.clear:
    try:
        client.delete_collection("reddit_topics")
        print("Cleared existing collection")
    except:
        print("No existing collection to clear")

# get or create collection
collection = client.get_or_create_collection(
    name="reddit_topics",
    metadata={"hnsw:space": "cosine"}
)

# format data
documents = data["top_trends"]
embeddings = [model.encode(doc).tolist() for doc in documents]
metadatas = [{"date": data["date"], "source": "trends"} for _ in documents]

# use upsert for append mode, add for fresh/clear mode
import uuid
ids = [str(uuid.uuid4()) for _ in documents]
collection.add(documents=documents, embeddings=embeddings, ids=ids, metadatas=metadatas)
print(f"Appended {len(documents)} trends")

print(f"Date: {data['date']}")
print(f"Total items in collection: {collection.count()}")
