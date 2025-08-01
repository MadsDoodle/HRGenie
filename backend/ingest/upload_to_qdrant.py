import os
import json
import logging
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

# --- Basic Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Environment and Constants ---
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "policy_chunks")
EMBEDDINGS_FOLDER = os.path.join(os.getcwd(), "qdrant_ready_embeddings")  # ✅ Use formatted folder

# --- Qdrant Client ---
client = QdrantClient(url=QDRANT_URL)

def create_collection():
    """Ensures the Qdrant collection exists."""
    try:
        collections = [c.name for c in client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            logging.info(f"✅ Created collection: '{COLLECTION_NAME}'")
        else:
            logging.info(f"Collection '{COLLECTION_NAME}' already exists.")
    except Exception as e:
        logging.error(f"❌ Could not check or create collection: {e}")
        raise

def load_and_upload_embeddings():
    """Loads embeddings from JSON files and upserts them into the Qdrant collection."""
    for filename in os.listdir(EMBEDDINGS_FOLDER):
        if filename.endswith(".json"):
            filepath = os.path.join(EMBEDDINGS_FOLDER, filename)
            logging.info(f"📁 Processing file: {filename}")
            try:
                with open(filepath, "r") as f:
                    chunks = json.load(f)

                points = []
                for chunk in chunks:
                    try:
                        points.append(
                            PointStruct(
                                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["id"])),  # UUID from ID
                                vector=chunk["vector"],
                                payload=chunk["payload"]
                            )
                        )
                    except Exception as chunk_err:
                        logging.warning(f"⚠️ Skipping bad chunk in {filename}: {chunk_err}")

                if not points:
                    logging.warning(f"⚠️ No valid points in {filename}, skipping.")
                    continue

                client.upsert(collection_name=COLLECTION_NAME, points=points)
                logging.info(f"⬆️  Uploaded {len(points)} vectors from {filename}")

            except json.JSONDecodeError:
                logging.error(f"❌ Error decoding JSON from file: {filename}")
            except Exception as e:
                logging.error(f"❌ Unexpected error with {filename}: {e}")

if __name__ == "__main__":
    logging.info("🚀 Starting embedding upload process...")
    create_collection()
    load_and_upload_embeddings()
    logging.info("✅ Done. All embeddings processed.")
