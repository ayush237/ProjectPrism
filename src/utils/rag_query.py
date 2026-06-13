import os
import argparse
import chromadb
from google import genai
import logging
from dotenv import load_dotenv

load_dotenv()
from utils.logger import get_logger
logger = get_logger(__name__)s: %(message)s')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VECTOR_STORE_DIR = os.path.join(ROOT_DIR, "src", "vector_store")

def query_rag(query_text, top_k=5):
    try:
        chroma_client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
        collection = chroma_client.get_collection(name="research_archive")
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {e}", exc_info=True)
        return

    from google.genai import types
    retry_config = types.HttpRetryOptions(
        initial_delay=2.0,
        attempts=5
    )
    genai_client = genai.Client(http_options={'retry_options': retry_config})
    
    try:
        response = genai_client.models.embed_content(
            model='text-embedding-004',
            contents=query_text
        )
        query_embedding = response.embeddings[0].values
    except Exception as e:
        logger.error(f"Failed to embed query: {e}", exc_info=True)
        return
        
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        print(f"\n--- Top {top_k} Results for: '{query_text}' ---\n")
        
        for i in range(len(results['ids'][0])):
            doc_id = results['ids'][0][i]
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i]
            distance = results['distances'][0][i]
            
            filename = metadata.get('filename', 'Unknown')
            
            print(f"[{i+1}] Source: {filename} (Distance: {distance:.4f})")
            print(f"Content:\n{document}\n")
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"Failed to query collection: {e}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the RAG Vector Lakehouse")
    parser.add_argument("query", type=str, help="The search query string")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return")
    args = parser.parse_args()
    
    query_rag(args.query, args.top_k)
