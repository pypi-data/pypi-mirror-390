"""Configuration management for semantic search MCP server."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for semantic search operations."""

    # Required settings (no defaults)
    openai_api_key: str
    neo4j_password: str

    # OpenAI settings (with defaults)
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Neo4j settings (with defaults)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"

    # Search settings (with defaults)
    default_limit: int = 10
    max_limit: int = 100


def load_config() -> Config:
    """Load configuration from environment variables."""

    # Required environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    neo4j_password = os.getenv("NEO4J_PASSWORD")
    if not neo4j_password:
        raise ValueError("NEO4J_PASSWORD environment variable is required")

    # Optional environment variables with defaults
    config = Config(
        openai_api_key=openai_api_key,
        neo4j_password=neo4j_password,
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        default_limit=int(os.getenv("DEFAULT_LIMIT", "10")),
        max_limit=int(os.getenv("MAX_LIMIT", "100")),
    )

    return config
