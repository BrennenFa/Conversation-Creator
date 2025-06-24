from openai import OpenAI
import chromadb
from chromadb.config import Settings

model = SentenceTransformer("all-MiniLM-L6-v2")

# reconnect to db
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="db/" 
))

collection = client.get_collection(name="tweets")

query_text = "Give me some conversation starters based on relevant topics"
query_embedding = model.encode([query_text])
