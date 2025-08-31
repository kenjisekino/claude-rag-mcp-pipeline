import streamlit as st
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_system import ConversationalRAGSystem

# Page configuration
st.set_page_config(
    page_title="Conversational Claude RAG",
    page_icon="💬",
    layout="wide"
)

# Initialize RAG system
@st.cache_resource
def load_rag_system():
    return ConversationalRAGSystem(embedding_provider="openai")

def main():
    st.title("💬 Conversational Claude RAG Pipeline")
    st.write("Chat with Claude about your documents with full conversation memory!")
    
    rag = load_rag_system()
    
    # Initialize session state for conversation
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for system management
    st.sidebar.header("🔧 System Management")
    
    # Document ingestion (same as before)
    st.sidebar.subheader("📄 Document Management")
    docs_directory = st.sidebar.text_input("Documents Directory Path", "./documents")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📥 Ingest Documents"):
            if os.path.exists(docs_directory):
                with st.spinner("Processing documents..."):
                    success = rag.ingest_documents(docs_directory)
                if success:
                    st.sidebar.success("Documents ingested successfully!")
                    st.rerun()
                else:
                    st.sidebar.error("No documents found or processing failed!")
            else:
                st.sidebar.error("Directory not found!")
    
    with col2:
        if st.button("🗑️ Clear Database"):
            rag.clear_database()
            st.sidebar.success("Database cleared!")
            st.rerun()
    
    # NEW: Conversation management
    st.sidebar.subheader("💬 Conversation")
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        if st.button("🔄 Clear Chat"):
            st.session_state.messages = []
            rag.clear_conversation()
            st.rerun()
    
    with col4:
        conversation_summary = rag.get_conversation_summary()
        st.write(f"📊 {conversation_summary}")
    
    # System stats
    stats = rag.get_system_stats()
    st.sidebar.metric("Total Documents", stats['total_documents'])
    
    # Main chat interface
    st.header("💬 Chat with Your Documents")
    
    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander("📚 Sources Used"):
                        for i, source in enumerate(message["sources"], 1):
                            st.write(f"📄 {i}. {source['source']}")


    # Replace the query processing section with:
    if prompt := st.chat_input("Ask any question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching and thinking..."):
                if stats['total_documents'] == 0:
                    # No documents - use general knowledge
                    response_text = rag.llm_service.generate_simple_response(prompt)
                    sources = []
                    mode = "general_knowledge"
                else:
                    # Hybrid mode
                    result = rag.query_hybrid(prompt, n_results=5)
                    response_text = result['answer']
                    sources = result['sources']
                    mode = result['mode']
                
                st.write(response_text)
                
                # Show mode indicator
                if mode == "document_based":
                    st.info("📚 Answer based on your documents")
                    if sources:
                        with st.expander("📄 Sources Used"):
                            for i, source in enumerate(sources, 1):
                                st.write(f"{i}. {source['source']}")
                else:
                    st.info("🧠 Answer based on general knowledge (no relevant documents found)")
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text,
            "sources": sources,
            "mode": mode
        })
    
if __name__ == "__main__":
    main()