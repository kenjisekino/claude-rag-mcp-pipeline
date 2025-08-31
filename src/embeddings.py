import openai
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self, provider="openai"):
        self.provider = provider
        
        if provider == "openai":
            self.client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif provider == "local":
            # Load local embedding model
            print("Loading local embedding model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_embedding(self, text):
        """Get embedding for a single text"""
        if self.provider == "openai":
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        
        elif self.provider == "local":
            return self.model.encode(text).tolist()
    
    def get_embeddings_batch(self, texts, batch_size=100):
        """Get embeddings for multiple texts"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            if self.provider == "openai":
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=batch
                )
                batch_embeddings = [data.embedding for data in response.data]
            
            elif self.provider == "local":
                batch_embeddings = self.model.encode(batch).tolist()
            
            embeddings.extend(batch_embeddings)
            print(f"Processed {min(i + batch_size, len(texts))}/{len(texts)} embeddings")
        
        return embeddings