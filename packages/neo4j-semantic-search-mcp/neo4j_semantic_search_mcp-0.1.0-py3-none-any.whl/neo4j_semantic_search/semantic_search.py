"""Semantic search engine for Neo4j knowledge graph."""

from typing import List, Dict, Any, Optional
from openai import OpenAI
from neo4j import GraphDatabase, Driver
from dataclasses import dataclass

from .config import Config


@dataclass
class SearchResult:
    """Result from semantic search."""

    id: str  # Node or edge ID
    labels: List[str]  # Node labels or relationship type
    properties: Dict[str, Any]  # All properties
    similarity_score: float


@dataclass
class VectorIndexInfo:
    """Information about a vector index in Neo4j."""

    name: str
    labels: List[str]
    properties: List[str]
    entity_property: str  # The property being indexed


class SemanticSearchEngine:
    """Semantic search engine using OpenAI embeddings and Neo4j vector indexes."""

    def __init__(self, config: Config):
        """Initialize the semantic search engine.

        Args:
            config: Configuration object with API keys and settings
        """
        self.config = config
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        self.neo4j_driver = GraphDatabase.driver(
            config.neo4j_uri, auth=(config.neo4j_user, config.neo4j_password)
        )

    def close(self):
        """Close connections."""
        self.neo4j_driver.close()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        response = self.openai_client.embeddings.create(
            model=self.config.embedding_model, input=text
        )
        return response.data[0].embedding

    def semantic_search(
        self,
        query: str,
        limit: int = None,
        threshold: float = 0.7,
    ) -> List[SearchResult]:
        """Search all vector indexes for nodes/edges matching the query.

        Args:
            query: Natural language query
            limit: Maximum number of results (default from config)
            threshold: Minimum similarity score (0-1, default 0.7)

        Returns:
            List of SearchResult objects sorted by similarity score
        """
        if limit is None:
            limit = self.config.default_limit

        # Cap at max limit
        limit = min(limit, self.config.max_limit)

        # Generate embedding once
        query_embedding = self.generate_embedding(query)

        # Get all available indexes
        indexes = self.list_available_indexes()

        if not indexes:
            return []

        all_results = []

        # Search each index
        for index_info in indexes:
            try:
                results = self._search_index(
                    index_info.name, query_embedding, limit, threshold
                )
                all_results.extend(results)
            except Exception as e:
                print(f"Warning: Failed to search index {index_info.name}: {e}")
                continue

        # Sort by score and return top results
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return all_results[:limit]

    def _search_index(
        self,
        index_name: str,
        embedding: List[float],
        limit: int,
        threshold: float,
    ) -> List[SearchResult]:
        """Search a single vector index.

        Args:
            index_name: Name of the vector index
            embedding: Query embedding vector
            limit: Maximum results
            threshold: Minimum similarity score

        Returns:
            List of SearchResult objects
        """
        with self.neo4j_driver.session() as session:
            query = """
                CALL db.index.vector.queryNodes($index_name, $limit, $query_vector)
                YIELD node, score
                WHERE score >= $threshold
                RETURN elementId(node) AS id,
                       labels(node) AS labels,
                       properties(node) AS properties,
                       score
                ORDER BY score DESC
            """

            result = session.run(
                query,
                index_name=index_name,
                limit=limit,
                query_vector=embedding,
                threshold=threshold,
            )

            results = []
            for record in result:
                search_result = SearchResult(
                    id=record["id"],
                    labels=record["labels"],
                    properties=dict(record["properties"]),
                    similarity_score=float(record["score"]),
                )
                results.append(search_result)

            return results

    def list_available_indexes(self) -> List[VectorIndexInfo]:
        """Discover all vector indexes in Neo4j.

        Returns:
            List of VectorIndexInfo objects describing available indexes
        """
        with self.neo4j_driver.session() as session:
            result = session.run("""
                SHOW INDEXES
                YIELD name, type, labelsOrTypes, properties
                WHERE type = 'VECTOR'
                RETURN name, labelsOrTypes, properties
            """)

            indexes = []
            for record in result:
                index_info = VectorIndexInfo(
                    name=record["name"],
                    labels=record["labelsOrTypes"],
                    properties=record["properties"],
                    entity_property=record["properties"][0] if record["properties"] else "embedding"
                )
                indexes.append(index_info)

            return indexes
