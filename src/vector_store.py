import chromadb
from chromadb.config import Settings
import uuid

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "claude_document_collection"
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(self.collection_name)
            print(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, chunks, embeddings):
        """Add document chunks with embeddings to vector store"""
        ids = [chunk['chunk_id'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [{'source': chunk['source'], 'file_path': chunk['file_path']} 
                    for chunk in chunks]
        
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(chunks)} chunks to vector store")
    
    def query(self, query_text, embedding_service, n_results=5):
        """Search for similar documents"""
        query_embedding = embedding_service.get_embedding(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return {
            'documents': results['documents'][0],
            'metadatas': results['metadatas'][0],
            'distances': results['distances'][0]
        }
    
    def get_stats(self):
        """Get collection statistics"""
        return {
            'total_documents': self.collection.count(),
            'collection_name': self.collection_name
        }
    
    def clear_collection(self):
        """Clear all documents from collection (useful for testing)"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(self.collection_name)
        print("Cleared collection")