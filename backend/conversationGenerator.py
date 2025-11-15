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

# Get or create collection
collection = client.get_or_create_collection(
    name="reddit_topics",
    metadata={"hnsw:space": "cosine"}
)

# Create query and encode it
query = "Generate Conversation Topics"
vector = model.encode(query).tolist()

print("Starting Query")

# 30 days previous
cutoffDate = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")


# Query Chroma
results = collection.query(
    query_embeddings=[vector],
    n_results=10,
    where={"date": {"$gte": cutoffDate}}
)

# Extract text from results
context = "\n\n".join(results['documents'][0])




# Step 3: Use Gemini to generate conversation topics
prompt = f"""You are an expert summarizer. Use the information below to answer the user's question.

Context:
{context}

Question:
{query}

Answer:"""

# Initialize Gemini model and generate response
gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
response = gemini_model.generate_content(prompt)
print(response.text)

