#!/usr/bin/env python3

import asyncio
import json
import sys
import os
from typing import Any, Sequence

# Set working directory and paths
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("Starting MCP server...", file=sys.stderr)

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from src.rag_system import ConversationalRAGSystem

# Initialize RAG system
print("Initializing RAG system...", file=sys.stderr)
rag_system = ConversationalRAGSystem(embedding_provider="openai")
print("RAG system ready", file=sys.stderr)

# Create server
server = Server("personal-documents")

@server.list_tools()
async def list_tools() -> list[Tool]:
    print("Tool list requested", file=sys.stderr)
    return [
        Tool(
            name="search_documents",
            description="Search through personal document collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query or question"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="document_stats",
            description="Get statistics about document collection",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    print(f"Tool called: {name}", file=sys.stderr)
    
    if name == "search_documents":
        query = arguments.get("query", "")
        print(f"Searching for: {query}", file=sys.stderr)
        
        try:
            result = rag_system.query(query, n_results=5)
            
            response = f"**Answer:** {result['answer']}\n\n"
            if result['sources']:
                sources = [s['source'] for s in result['sources']]
                response += f"**Sources:** {', '.join(sources)}"
            
            return [TextContent(type="text", text=response)]
        
        except Exception as e:
            error_msg = f"Error searching documents: {str(e)}"
            print(error_msg, file=sys.stderr)
            return [TextContent(type="text", text=error_msg)]
    
    elif name == "document_stats":
        try:
            stats = rag_system.get_system_stats()
            response = f"Document collection contains {stats['total_documents']} chunks"
            return [TextContent(type="text", text=response)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting stats: {str(e)}")]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    print("Starting stdio server...", file=sys.stderr)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("MCP server connected and running", file=sys.stderr)
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())