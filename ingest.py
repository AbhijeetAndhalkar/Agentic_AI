import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "chatbot")

print(f"Loaded API Key: {PINECONE_API_KEY[:5]}...")

def initialize_pinecone():
    print("Initializing Pinecone...")
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        return pc
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")
        return None

def get_embedding_model():
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model
    except Exception as e:
        print(f"Error loading embedding model: {e}")
        return None

def create_index_if_not_exists(pc, index_name):
    try:
        existing_indexes = [index.name for index in pc.list_indexes()]
        if index_name in existing_indexes:
            print(f"Index {index_name} already exists. Deleting to ensure correct dimension...")
            pc.delete_index(index_name)
            time.sleep(5)  # Wait for deletion

        print(f"Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=384,  # Dimension for all-MiniLM-L6-v2
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        time.sleep(10) # Wait for index initialization
    except Exception as e:
        print(f"Error creating index: {e}")

def ingest_data():
    pc = initialize_pinecone()
    if not pc:
        return

    create_index_if_not_exists(pc, PINECONE_INDEX_NAME)
    index = pc.Index(PINECONE_INDEX_NAME)

    model = get_embedding_model()
    if not model:
        return


    try:
        with open("linkcode.txt", "r", encoding="utf-8") as f:
            # Read lines and filter out empty ones
            lines = [line.strip() for line in f if line.strip()]
            scraped_data = [{"id": f"doc_{i}", "text": line} for i, line in enumerate(lines)]
    except Exception as e:
        print(f"Error reading linkcode.txt: {e}")
        return


    vectors = []
    print("Generating embeddings...")
    for item in scraped_data:
        embedding = model.encode(item['text']).tolist()
        vectors.append({
            "id": item['id'],
            "values": embedding,
            "metadata": {"text": item['text']}
        })

    print(f"Upserting {len(vectors)} vectors to Pinecone...")
    try:
        index.upsert(vectors=vectors)
        print("Ingestion complete!")
    except Exception as e:
        print(f"Error upserting data: {e}")

if __name__ == "__main__":
    if not PINECONE_API_KEY:
        print("Error: PINECONE_API_KEY not found in .env file.")
    else:
        ingest_data()
