from sentence_transformers import SentenceTransformer
import os
from qdrant_client import QdrantClient
import openai
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


load_dotenv()

HUGGING_FACE=os.getenv("HUGGING_FACE")


model = SentenceTransformer("all-MiniLM-L6-v2")
qClient = QdrantClient(path=os.getenv("DB_DIR"))

query = "Generate Conversation Topics"
vector = model.encode(query).tolist()

results = qClient.search(
    collection_name="reddit_topics",
    query_vector=vector,
    limit=10,
    with_payload=True
)


context = "\n\n".join(hit.payload["text"] for hit in results)





# Step 3: Use LLM to generate an answer
prompt = f"""You are an expert summarizer. Use the information below to answer the user's question.

Context:
{context}

Question:
{query}

# Answer:"""


model_name = "MiniMaxAI/SynLogic-Mix-3-32B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="auto")

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=20)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

