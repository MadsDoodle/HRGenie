import os
import json
import logging
from pathlib import Path
from typing import List, Dict
import openai
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()


# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- Constants ---
CHUNKS_DIR = Path("docs_chunks")  
EMBEDDINGS_DIR = Path("embeddings") #create embeddings folder before hand
EMBEDDING_MODEL = "text-embedding-3-small"

# --- Ensure directory exists ---
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

# --- Load OpenAI Key ---
openai.api_key = os.getenv("OPENAI_API_KEY")  # safer to use env var

if not openai.api_key:
    raise ValueError(" OPENAI_API_KEY not found. Set it as an environment variable.")

# --- Load Chunked JSON ---
def load_chunks_from_file(filepath: Path) -> List[Dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Embed text using OpenAI ---
def get_embedding(text: str) -> List[float]:
    try:
        response = openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error embedding text: {e}")
        return []

# --- Main embedding logic ---
def embed_all_documents():
    json_files = list(CHUNKS_DIR.glob("*.json"))
    logger.info(f" Found {len(json_files)} documents in {CHUNKS_DIR}")

    for json_file in tqdm(json_files, desc="Embedding documents"):
        logger.info(f" Processing: {json_file.name}")

        chunks = load_chunks_from_file(json_file)
        embedded_chunks = []

        for chunk in chunks:
            text = chunk.get("text", "")
            if not text.strip():
                continue

            chunk_type = chunk.get("metadata", {}).get("type", "text")
            if chunk_type == "table":
                text = f"Table data: {text}"  # Or run a table summarization step

            embedding = get_embedding(text)
            if not embedding:
                continue

            embedded_chunks.append({
                "id": chunk.get("id"),
                "text": text,
                "embedding": embedding,
                "metadata": {
                    **chunk.get("metadata", {}),
                    "source_file": json_file.name  # add this line
                }
            })


        # Save to embeddings folder
        output_file = EMBEDDINGS_DIR / json_file.name
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(embedded_chunks, f, indent=2)

        logger.info(f" Saved embeddings to {output_file}")

if __name__ == "__main__":
    embed_all_documents()



