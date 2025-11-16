from sentence_transformers import SentenceTransformer
import os
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timedelta

load_dotenv()
print("yes its running")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")

# Get list of all collections
all_collections = client.list_collections()
print(f"Available collections: {[col.name for col in all_collections]}")

# Create query and encode it
query = "Generate Conversation Topics"
vector = model.encode(query).tolist()

print("Starting Query")

cutoffDate = (datetime.now() - timedelta(days=30)).isoformat()

all_documents = []
for collection in all_collections:
    # Get count to know how many to request
    count = collection.count()
    print(f"Querying {collection.name} ({count} total documents)...")

    # Request all documents (or max of 100 for performance)
    n = min(count, 100)

    # Query without date filter for now since scraped_at is a string
    results = collection.query(
        query_embeddings=[vector],
        n_results=n
    )

    if results['documents'][0]:
        all_documents.extend(results['documents'][0])

# Extract text from results
context = "\n\n".join(all_documents)
print(f"\nTotal documents retrieved: {len(all_documents)}")




# Step 3: Use Gemini to generate conversation topics
prompt = f"""You are a professor who just had a massive scandal but you are innocent. You need to talk to the judge of the court
case to get out. List out some conversation topics to get you guys talking

Context:
{context}

Question:
{query}

Answer:"""

# Initialize Gemini model and generate response
gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
response = gemini_model.generate_content(prompt)
print(response.text)

