import os
import json
import logging
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Title, Table
import re

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("chunking.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Input/output directories
DATA_DIR = Path("data")
CHUNKS_DIR = Path("docs_chunks")
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENTS = {
    "hr_leave_policy": "HR Leave Policy.pdf",
    "hr_travel_policy": "HR Travel Policy.pdf",
    "sample_offer_letter": "HR Offer Letter.pdf"
}

def looks_like_section_title(text):
    """Heuristic to detect section titles."""
    return bool(re.match(r'^(\d+[\.\d+]*|[📘🧠🏢📄🛫🧱📋🏡])', text.strip()))

def chunk_elements(elements):
    """
    Chunk elements into structured sections using Titles and Tables.
    """
    chunks = []
    current_section_title = None
    current_chunk_elements = []

    for i, element in enumerate(elements):
        if isinstance(element, Title):
            next_is_table = (i + 1 < len(elements) and isinstance(elements[i+1], Table))
            short_and_alpha = len(element.text.split()) < 5 and any(char.isalpha() for char in element.text)

            if next_is_table or short_and_alpha:
                # Likely a table caption or short heading – don't treat as new section
                continue

            # Finalize previous chunk
            if current_chunk_elements:
                chunks.append({
                    "section_title": current_section_title or "Untitled Section",
                    "type": "text",
                    "text": "\n".join([e.text for e in current_chunk_elements if hasattr(e, 'text') and e.text.strip()])
                })
                current_chunk_elements = []

            current_section_title = element.text

        elif isinstance(element, Table):
            # Flush any text before table
            if current_chunk_elements:
                chunks.append({
                    "section_title": current_section_title or "Untitled Section",
                    "type": "text",
                    "text": "\n".join([e.text for e in current_chunk_elements if hasattr(e, 'text') and e.text.strip()])
                })
                current_chunk_elements = []

            # Only add non-empty table
            if element.text and element.text.strip():
                chunks.append({
                    "section_title": current_section_title or f"Table Section (Page {element.metadata.get('page_number', '?')})",
                    "type": "table",
                    "text": element.text.strip()
                })

        else:
            current_chunk_elements.append(element)

    # Finalize last chunk
    if current_chunk_elements:
        chunks.append({
            "section_title": current_section_title or "Untitled Section",
            "type": "text",
            "text": "\n".join([e.text for e in current_chunk_elements if hasattr(e, 'text') and e.text.strip()])
        })

    return chunks

def chunk_document(doc_name: str, filename: str):
    file_path = DATA_DIR / filename
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return

    logger.info(f"Processing document: {file_path}")
    logger.info("=" * 60)

    try:
        elements = partition_pdf(
            filename=str(file_path),
            extract_images_in_pdf=True,
            infer_table_structure=True,
            strategy="fast"
        )

        raw_chunks = chunk_elements(elements)

        chunk_data = []
        for i, chunk in enumerate(raw_chunks):
            chunk_data.append({
                "id": f"{doc_name}_chunk_{i+1}",
                "text": chunk["text"],
                "metadata": {
                    "source": doc_name,
                    "chunk_index": i,
                    "section_title": chunk["section_title"],
                    "type": chunk["type"]
                }
            })

        output_file = CHUNKS_DIR / f"{doc_name}_chunks.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Created {len(chunk_data)} chunks for {doc_name}, saved to {output_file}")

    except Exception as e:
        logger.error(f"❌ Error processing {doc_name}: {str(e)}")

def main():
    for doc_name, filename in DOCUMENTS.items():
        chunk_document(doc_name, filename)

if __name__ == "__main__":
    main()
    logger.info("✅ All documents processed successfully.")
