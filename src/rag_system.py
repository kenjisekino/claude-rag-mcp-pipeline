import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.document_processor import DocumentProcessor
from src.embeddings import EmbeddingService
from src.vector_store import VectorStore
from src.llm_service import LLMService

class ConversationalRAGSystem:
    def __init__(self, embedding_provider="openai"):
        print("Initializing Conversational Claude RAG System...")
        self.doc_processor = DocumentProcessor()
        self.embedding_service = EmbeddingService(provider=embedding_provider)
        self.vector_store = VectorStore()
        self.llm_service = LLMService()
        
        # NEW: Conversation management
        self.conversation_history = []
        self.max_history_length = 10  # Keep last 10 exchanges
        
        print("System initialized successfully!")
    
    def query(self, question, n_results=5, session_id="default"):
        """Query with conversation memory"""
        print(f"Processing conversational query: {question}")
        
        # Retrieve relevant documents
        results = self.vector_store.query(question, self.embedding_service, n_results)
        
        if not results['documents']:
            response = "No relevant documents found in the database. Please add some documents first."
        else:
            print(f"Found {len(results['documents'])} relevant chunks")
            
            # Generate response with conversation history
            response = self.llm_service.generate_conversational_response(
                question, 
                results, 
                self.conversation_history
            )
        
        # Store conversation exchange
        self._add_to_history(question, response)
        
        return {
            'answer': response,
            'sources': results['metadatas'] if results['documents'] else [],
            'retrieved_chunks': results['documents'] if results['documents'] else [],
            'similarity_scores': results['distances'] if results['documents'] else [],
            'conversation_turn': len(self.conversation_history)
        }
    
    def query_hybrid(self, question, n_results=5, relevance_threshold=0.7):
        """Query with hybrid document/general knowledge mode"""
        print(f"Processing hybrid query: {question}")
        
        # Always try to retrieve relevant documents first
        results = self.vector_store.query(question, self.embedding_service, n_results)
        
        # Use hybrid response generation
        response = self.llm_service.generate_hybrid_response(
            question, 
            results, 
            self.conversation_history,
            relevance_threshold
        )
        
        # Determine response mode
        has_relevant_docs = (
            results['documents'] and 
            len(results['distances']) > 0 and 
            min(results['distances']) < relevance_threshold
        )
        
        mode = "document_based" if has_relevant_docs else "general_knowledge"
        
        # Store conversation exchange
        self._add_to_history(question, response)
        
        return {
            'answer': response,
            'sources': results['metadatas'] if has_relevant_docs else [],
            'retrieved_chunks': results['documents'] if has_relevant_docs else [],
            'similarity_scores': results['distances'] if has_relevant_docs else [],
            'mode': mode,
            'conversation_turn': len(self.conversation_history)
        }
    
    def _add_to_history(self, question, response):
        """Add exchange to conversation history"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response
        })
        
        # Keep history manageable
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("Conversation history cleared")
    
    def get_conversation_summary(self):
        """Get summary of current conversation"""
        if not self.conversation_history:
            return "No conversation history"
        
        return f"{len(self.conversation_history)} exchanges in current conversation"
    
    # Keep all existing methods from your original rag_system.py
    def ingest_documents(self, directory_path):
        """Complete document ingestion pipeline"""
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} not found!")
            return False
        
        print("Step 1: Processing documents...")
        chunks = self.doc_processor.process_directory(directory_path)
        
        if not chunks:
            print("No documents found or processed successfully.")
            return False
        
        print(f"Found {len(chunks)} document chunks")
        
        print("Step 2: Generating embeddings...")
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_service.get_embeddings_batch(texts)
        
        print("Step 3: Storing in vector database...")
        self.vector_store.add_documents(chunks, embeddings)
        
        print(f"Ingestion complete! Added {len(chunks)} chunks to the database.")
        return True
    
    def test_claude_connection(self):
        """Test Claude API connection"""
        try:
            response = self.llm_service.generate_simple_response("Hello, Claude! Please respond with 'Connection successful!'")
            return True, response
        except Exception as e:
            return False, str(e)
    
    def get_system_stats(self):
        """Get system statistics"""
        return self.vector_store.get_stats()
    
    def clear_database(self):
        """Clear all documents from the database"""
        self.vector_store.clear_collection()