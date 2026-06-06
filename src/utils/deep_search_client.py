import os
import logging
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class DeepSearchClient:
    """
    Utility class for the Researcher Agent to perform autonomous Google Search grounding 
    via the Gemini API.
    """
    def __init__(self, model_name="gemini-2.5-pro"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logging.warning("GEMINI_API_KEY environment variable is not set. Client may fail if not authenticated via other means.")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
    def search(self, query: str) -> str:
        logging.info(f"Executing Deep Search Query via {self.model_name}: '{query}'")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                )
            )
            return response.text
        except Exception as e:
            logging.error(f"Deep Search failed: {e}")
            return f"Error executing deep search: {e}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test the Deep Search Client")
    parser.add_argument("--query", type=str, required=True, help="The query to search")
    args = parser.parse_args()
    
    client = DeepSearchClient()
    result = client.search(args.query)
    print("\n=== SEARCH RESULT ===")
    print(result)
