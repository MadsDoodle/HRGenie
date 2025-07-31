import os
import json
import logging
from tqdm import tqdm

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- Directories ---
INPUT_DIR = "embeddings"  # Folder with raw embedding JSON files
OUTPUT_DIR = "qdrant_ready_embeddings"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Transformation Process ---
for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"❌ Failed to read {filename}: {e}")
            continue

        formatted_points = []
        for item in tqdm(data, desc=f"Processing {filename}"):
            if not item.get("embedding") or not isinstance(item["embedding"], list):
                logging.warning(f"⚠️ Skipping invalid embedding for ID: {item.get('id')}")
                continue

            payload = {
                "text": item.get("text", ""),
                **item.get("metadata", {})
            }

            formatted = {
                "id": item["id"],
                "vector": item["embedding"],
                "payload": payload
            }
            formatted_points.append(formatted)

        try:
            out_path = os.path.join(OUTPUT_DIR, filename)
            with open(out_path, "w") as out_f:
                json.dump(formatted_points, out_f, indent=2)
            logging.info(f"✅ Transformed and saved: {filename}")
        except Exception as e:
            logging.error(f"❌ Failed to save {filename}: {e}")
