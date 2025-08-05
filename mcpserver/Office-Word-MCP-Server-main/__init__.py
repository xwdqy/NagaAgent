"""Office Word MCP Server package entry point."""
from .word_mcp_adapter import create_word_document_mcp_server, WordDocumentMCPServer

__all__ = ["create_word_document_mcp_server", "WordDocumentMCPServer"]
