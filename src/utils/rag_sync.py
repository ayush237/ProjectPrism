import os
import chromadb
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv()
from utils.logger import get_logger
logger = get_logger(__name__)s: %(message)s')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VECTOR_STORE_DIR = os.path.join(ROOT_DIR, "src", "vector_store")
DIRS_TO_SCAN = [
    os.path.join(ROOT_DIR, "reference_material"),
    os.path.join(ROOT_DIR, "docs", "research_archive")
]

def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def sync():
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    try:
        chroma_client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
        collection = chroma_client.get_or_create_collection(name="research_archive")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}", exc_info=True)
        return

    from google.genai import types
    retry_config = types.HttpRetryOptions(
        initial_delay=2.0,
        attempts=5
    )
    genai_client = genai.Client(http_options={'retry_options': retry_config})
    
    for scan_dir in DIRS_TO_SCAN:
        if not os.path.exists(scan_dir):
            logger.warning(f"Directory not found, skipping: {scan_dir}")
            continue
            
        for root, _, files in os.walk(scan_dir):
            for file in files:
                if not (file.endswith(".md") or file.endswith(".txt")):
                    continue
                    
                filepath = os.path.join(root, file)
                current_mtime = os.path.getmtime(filepath)
                
                # Check ChromaDB to see if file needs updating
                existing_docs = collection.get(
                    where={"filename": filepath},
                    include=["metadatas"]
                )
                
                needs_update = True
                if existing_docs and existing_docs["metadatas"]:
                    # Assume all chunks have the same last_modified, check the first
                    last_synced_mtime = existing_docs["metadatas"][0].get("last_modified", 0)
                    if current_mtime <= last_synced_mtime:
                        needs_update = False
                        
                if needs_update:
                    logger.info(f"Syncing updated/new file: {filepath}")
                    # Delete existing vectors for this file
                    if existing_docs and existing_docs["ids"]:
                        collection.delete(where={"filename": filepath})
                        
                    # Read and chunk
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            text = f.read()
                    except Exception as e:
                        logger.error(f"Failed to read {filepath}: {e}", exc_info=True)
                        continue
                        
                    chunks = chunk_text(text)
                    if not chunks:
                        continue
                        
                    # Generate embeddings and insert
                    try:
                        embeddings = []
                        for chunk in chunks:
                            response = genai_client.models.embed_content(
                                model='text-embedding-004',
                                contents=chunk
                            )
                            embeddings.append(response.embeddings[0].values)
                        
                        ids = [f"{filepath}_chunk_{i}" for i in range(len(chunks))]
                        metadatas = [{"filename": filepath, "last_modified": current_mtime} for _ in chunks]
                        
                        collection.add(
                            ids=ids,
                            embeddings=embeddings,
                            documents=chunks,
                            metadatas=metadatas
                        )
                        logger.info(f"Successfully inserted {len(chunks)} chunks for {filepath}")
                    except Exception as e:
                        logger.error(f"Failed to embed/insert chunks for {filepath}: {e}", exc_info=True)

if __name__ == "__main__":
    sync()
