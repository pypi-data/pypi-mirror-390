"""MCP server for semantic search on Neo4j knowledge graph."""

import sys
import json
import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import load_config
from .semantic_search import SemanticSearchEngine


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server
app = Server("semantic-search")

# Global engine instance (initialized on startup)
engine: SemanticSearchEngine = None


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available semantic search tools."""
    return [
        Tool(
            name="semantic_search",
            description="""Search across all vector indexes in the Neo4j knowledge graph.

This tool is completely schema-agnostic and works with ANY Neo4j knowledge graph that has embeddings.

How it works:
1. Auto-discovers all vector indexes in your database
2. Generates embedding for your natural language query
3. Searches all indexes and returns matches above the threshold
4. Returns nodes (or edges) sorted by semantic similarity

Example queries:
- "database failures"
- "kubernetes scaling issues"
- "monitoring alerts"
- "cache problems"

Returns any nodes/edges that match, regardless of type or schema.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query describing what you're looking for",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10, max: 100)",
                        "default": 10,
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Minimum similarity score (0-1, default: 0.7). Higher = more strict matching.",
                        "default": 0.7,
                    },
                },
                "required": ["query"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool invocations."""
    try:
        if name == "semantic_search":
            return await handle_semantic_search(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}",
            )
        ]


async def handle_semantic_search(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle semantic_search tool invocation."""
    query = arguments["query"]
    limit = arguments.get("limit", 10)
    threshold = arguments.get("threshold", 0.7)

    logger.info(f"Semantic search: query='{query}', limit={limit}, threshold={threshold}")

    # Perform search across all indexes
    results = engine.semantic_search(
        query=query,
        limit=limit,
        threshold=threshold,
    )

    # Format results
    if not results:
        response_text = f"No results found matching '{query}' with similarity >= {threshold}\n\nTry:\n- Lowering the threshold (current: {threshold})\n- Using different search terms\n- Checking that vector indexes exist and embeddings are populated"
    else:
        response_lines = [f"Found {len(results)} results matching '{query}':\n"]

        for i, result in enumerate(results, 1):
            # Format labels
            labels_str = ", ".join(result.labels) if result.labels else "Unknown"

            # Get name from properties if available
            name = result.properties.get("name", result.properties.get("id", "Unnamed"))

            line = f"{i}. **{name}** [{labels_str}] (similarity: {result.similarity_score:.3f})"

            # Show a few key properties
            if "frequency" in result.properties:
                line += f" - mentioned {result.properties['frequency']} times"

            response_lines.append(line)

        response_text = "\n".join(response_lines)

    return [TextContent(type="text", text=response_text)]


async def main():
    """Main entry point for the MCP server."""
    global engine

    logger.info("Starting semantic search MCP server...")

    # Load configuration
    try:
        config = load_config()
        logger.info(f"Configuration loaded: Neo4j={config.neo4j_uri}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Initialize search engine
    try:
        engine = SemanticSearchEngine(config)
        logger.info("Semantic search engine initialized")
    except Exception as e:
        logger.error(f"Failed to initialize search engine: {e}")
        sys.exit(1)

    # Run MCP server
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    finally:
        if engine:
            engine.close()
            logger.info("Search engine closed")


def run():
    """Synchronous entry point for CLI."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    run()
