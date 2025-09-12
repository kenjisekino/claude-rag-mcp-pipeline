# Claude RAG Pipeline with MCP Integration

Retrieval Augmented Generation (RAG) system featuring conversational memory, hybrid knowledge modes, and Model Context Protocol (MCP) integration for document search functionality within Claude Desktop.

## Features

- **Complete RAG Pipeline**: Document processing, vector embeddings, semantic search, and LLM-powered responses
- **Conversational Memory**: Full ChatGPT-style conversations with context preservation across exchanges
- **Hybrid Knowledge Mode**: Ability to switch between document-based responses and general knowledge
- **Semantic Chunking**: Intelligent document segmentation that preserves meaning and context
- **MCP Integration**: Native Claude Desktop integration for document access functionality
- **Multi-format Support**: PDF, Word, Markdown, and plain text documents
- **Vector Database**: ChromaDB for efficient semantic search
- **Web Interface**: Streamlit app for document management and chat

## Architecture

```
Documents → Semantic Processing → Vector Embeddings → ChromaDB → Retrieval → Claude API → Response
                                                                        ↓
                                                                 MCP Protocol
                                                                        ↓
                                                                Claude Desktop
```

## Tech Stack

- **LLM**: Claude 3.5 (Anthropic API)
- **Embeddings**: OpenAI text-embedding-ada-002 or local sentence-transformers
- **Vector Database**: ChromaDB
- **Web Framework**: Streamlit
- **Document Processing**: PyPDF2, python-docx
- **Integration Protocol**: Model Context Protocol (MCP)

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Anthropic API key
- Claude Desktop app (for MCP integration)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/claude-rag-mcp-pipeline.git
cd claude-rag-mcp-pipeline
```

2. Create virtual environment:
```bash
python3 -m venv rag_env
source rag_env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

1. **Create documents folder**:
```bash
mkdir documents
```

2. **Add documents** to the `documents/` folder (PDF, Word, Markdown, or text files)

3. **Start the Streamlit app**:
```bash
streamlit run app.py
```

4. **Ingest documents** using the sidebar interface

5. **Chat with your documents** using the conversational interface

### MCP Integration (Advanced)

Connect your RAG system to Claude Desktop for native document access:

1. **Configure Claude Desktop** (create config file if it doesn't exist):
```bash
# Create the config file if it doesn't exist
mkdir -p "~/Library/Application Support/Claude"
touch "~/Library/Application Support/Claude/claude_desktop_config.json"
```

Edit the configuration file:
```json
// ~/.../Claude/claude_desktop_config.json
{
  "mcpServers": {
    "personal-documents": {
      "command": "/path/to/your/project/rag_env/bin/python",
      "args": ["/path/to/your/project/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your_key",
        "ANTHROPIC_API_KEY": "your_key"
      }
    }
  }
}
```

2. **Start the MCP server**:
```bash
python mcp_server.py
```

3. **Use Claude Desktop** - Chats will access your documents when relevant (e.g. try prompting "Can you search my documents for details regarding ...?"). Ensure "personal-documents" is enabled under "Search and tools".

## Project Structure

```
claude-rag-mcp-pipeline/
├── src/
│   ├── document_processor.py    # Document processing and semantic chunking
│   ├── embeddings.py           # Embedding generation (OpenAI/local)
│   ├── vector_store.py         # ChromaDB interface
│   ├── llm_service.py          # Claude API integration
│   └── rag_system.py           # Main RAG orchestration
├── documents/                  # Your documents go here
├── chroma_db/                 # Vector database (auto-created)
├── app.py                     # Streamlit web interface
├── mcp_server.py              # MCP protocol server
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md
```

## Key Components

### Document Processing
- **Multi-format support**: Handles PDF, Word, Markdown, and text files
- **Semantic chunking**: Preserves document structure and meaning
- **Metadata preservation**: Tracks source files and chunk locations

### Vector Search
- **Semantic similarity**: Finds relevant content by meaning, not keywords
- **Configurable retrieval**: Adjustable number of context chunks
- **Source attribution**: Clear tracking of information sources

### Conversational Interface
- **Memory persistence**: Maintains conversation context across exchanges
- **Hybrid responses**: Combines document knowledge with general AI capabilities
- **Source citation**: References specific documents in responses

### MCP Integration
- **Native Claude access**: Use Claude Desktop with your document knowledge
- **Automatic tool detection**: Claude recognizes when to search your documents
- **Secure local processing**: Documents never leave your machine

## Configuration

### Embedding Options
Switch between OpenAI embeddings and local models:
```python
# In src/rag_system.py
rag = ConversationalRAGSystem(embedding_provider="openai")  # or "local"
```

### Chunking Parameters
Adjust semantic chunking behavior:
```python
# In src/document_processor.py
chunks = self.semantic_chunk_llm(text, max_chunk_size=800, min_chunk_size=100)
```

### Response Tuning
Modify retrieval and response generation:
```python
# Number of chunks to retrieve
result = rag.query(question, n_results=5)

# Claude response length
response = llm_service.generate_response(query, chunks, max_tokens=600)
```

### Claude Model Selection
Change the Claude model version in `src/llm_service.py`:
```python
 # In LLMService class methods, update the model parameter (check console.anthropic.com for currently available models):
model="claude-3-5-haiku-latest"     # Fast, cost-effective  
model="claude-3-5-sonnet-latest"    # Higher quality reasoning
model="claude-3-opus-latest"        # Most capable
model="claude-4-sonnet-latest"      # If available
```

## Use Cases

- **Personal Knowledge Base**: Make your documents searchable and conversational
- **Research Assistant**: Query across multiple documents simultaneously
- **Document Analysis**: Extract insights from large document collections
- **Enterprise RAG**: Foundation for company-wide knowledge systems

## Technical Details

### Transformer Architecture Understanding
This system demonstrates practical implementation of:
- Vector embeddings for semantic representation
- Attention mechanisms through retrieval scoring
- Multi-step reasoning through conversation context
- Hybrid AI architectures combining retrieval and generation

## API Costs

**Typical monthly usage:**
- OpenAI embeddings: $2-10
- Claude API calls: $5-25
- **Total: $7-35/month for moderate usage**

**Cost reduction:**
- Use local embeddings (sentence-transformers) for free embedding generation
- Adjust response length limits
- Optimize chunk retrieval counts

## Production Considerations

### Current Implementation Scope
This system is designed for personal/single-user environments. However, the core RAG functionality, MCP integration, and conversational AI systems can be implemented at enterprise-level.

### Enterprise Production Deployment Requirements
To deploy this system in a true production enterprise environment, the following additions would be needed:

**Authentication & Authorization:**
- Multi-user authentication system (SSO integration)
- Role-based access controls (RBAC)
- Document-level permissions and access policies
- API key rotation and secure credential management

**Infrastructure & Scalability:**
- Container orchestration (Kubernetes deployment)
- Production-grade vector database (Pinecone, Weaviate, or managed ChromaDB)
- Load balancing and horizontal scaling
- Database clustering and replication
- CDN integration for document serving

**Monitoring & Operations:**
- Application performance monitoring (APM)
- Logging aggregation and analysis
- Health checks and alerting systems
- Usage analytics and cost tracking
- Backup and disaster recovery procedures

**Security Hardening:**
- Input validation and sanitization
- Rate limiting and DDoS protection
- Network security (VPC, firewalls, encryption in transit)
- Data encryption at rest
- Security audit trails and compliance logging

**Enterprise Integration:**
- Integration with existing identity providers
- Corporate data governance policies
- Compliance with data retention requirements
- Integration with enterprise monitoring/alerting systems
- Multi-tenancy support with resource isolation

**Cost Management:**
- Usage-based billing and chargeback systems
- Cost optimization and budget controls
- API usage monitoring and alerts
- Resource utilization optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built with:
- [Anthropic Claude](https://anthropic.com) for LLM capabilities
- [OpenAI](https://openai.com) for embedding models
- [ChromaDB](https://chromadb.com) for vector storage
- [Streamlit](https://streamlit.io) for web interface
- [Model Context Protocol](https://modelcontextprotocol.io) for Claude Desktop integration
