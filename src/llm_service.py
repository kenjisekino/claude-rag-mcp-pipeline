import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    def generate_conversational_response(self, query, retrieved_chunks, conversation_history, max_tokens=600):
        """Generate response with conversation context"""
        
        # Build context from retrieved chunks
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(retrieved_chunks['documents'], retrieved_chunks['metadatas']), 1):
            context_parts.append(f"Source {i} ({metadata['source']}):\n{doc}")
        
        context = "\n\n".join(context_parts)
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-3:]  # Last 3 exchanges
            history_parts = []
            for exchange in recent_history:
                history_parts.append(f"Previous Q: {exchange['question']}")
                history_parts.append(f"Previous A: {exchange['response'][:200]}...")  # Truncate long responses
            history_text = "\n".join(history_parts)
        
        # Create conversational prompt
        prompt = f"""You are having a conversation with a user about their personal documents. Here's the context:

<conversation_history>
{history_text if history_text else "This is the start of our conversation."}
</conversation_history>

<document_context>
{context}
</document_context>

<current_question>
{query}
</current_question>

Instructions:
- Answer the current question based on the document context and conversation history
- Reference previous parts of our conversation when relevant
- If the current question builds on previous questions, acknowledge that connection
- When citing information, indicate which source you're drawing from
- If the context doesn't contain enough information, say so clearly

Answer:"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating conversational response: {str(e)}"
    
    # Keep all existing methods
    def generate_response(self, query, retrieved_chunks, max_tokens=500):
        """Original non-conversational response method"""
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(retrieved_chunks['documents'], retrieved_chunks['metadatas']), 1):
            context_parts.append(f"Source {i} ({metadata['source']}):\n{doc}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""Based on the following context, please answer the question.

<context>
{context}
</context>

<question>
{query}
</question>

Please provide a comprehensive answer based on the context provided. When referencing information, indicate which source you're drawing from.

Answer:"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_simple_response(self, query, max_tokens=300):
        """Generate response without any context"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": query}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
        
    # Add this method to your existing LLMService class

    def generate_hybrid_response(self, query, retrieved_chunks, conversation_history, relevance_threshold=0.7, max_tokens=600):
        """Generate response using documents OR general knowledge"""
        
        # Check if retrieved chunks are relevant
        has_relevant_docs = (
            retrieved_chunks['documents'] and 
            len(retrieved_chunks['distances']) > 0 and 
            min(retrieved_chunks['distances']) < relevance_threshold
        )
        
        if has_relevant_docs:
            # Use document-based response
            return self.generate_conversational_response(query, retrieved_chunks, conversation_history, max_tokens)
        
        else:
            # Fall back to general knowledge with conversation context
            history_text = ""
            if conversation_history:
                recent_history = conversation_history[-3:]
                history_parts = []
                for exchange in recent_history:
                    history_parts.append(f"Previous Q: {exchange['question']}")
                    history_parts.append(f"Previous A: {exchange['response'][:200]}...")
                history_text = "\n".join(history_parts)
            
            prompt = f"""You are having a conversation with a user. Here's our conversation history:

    <conversation_history>
    {history_text if history_text else "This is the start of our conversation."}
    </conversation_history>

    <current_question>
    {query}
    </current_question>

    Note: I searched the user's personal document collection but didn't find relevant information for this question, so please answer based on your general knowledge. If appropriate, acknowledge that this information comes from your training rather than their specific documents.

    Answer:"""
            
            try:
                response = self.client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=max_tokens,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return response.content[0].text
                
            except Exception as e:
                return f"Error generating hybrid response: {str(e)}"