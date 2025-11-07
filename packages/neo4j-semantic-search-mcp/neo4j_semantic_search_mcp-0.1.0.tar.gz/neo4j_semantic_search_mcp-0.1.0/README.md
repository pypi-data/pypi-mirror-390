# Semantic Search MCP Server

**Universal, schema-agnostic** semantic search for **any** Neo4j knowledge graph.

One tool. Works everywhere. No configuration needed.

## What It Does

Searches across ALL vector indexes in your Neo4j database using semantic similarity. Returns anything that matches your natural language query above a threshold.

Works with:
- Any node type
- Any relationship type
- Any schema
- Any knowledge graph with embeddings

## Installation

### 1. Install Dependencies

```bash
pip install -r mcp_servers/semantic_search/requirements.txt
```

### 2. Configure Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."
export NEO4J_PASSWORD="your-password"

# Optional (defaults shown)
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export EMBEDDING_MODEL="text-embedding-3-small"
```

### 3. Register with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "semantic-search": {
      "command": "python",
      "args": ["-m", "mcp_servers.semantic_search.server"],
      "cwd": "/path/to/your/e2r-rd",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

## Usage

### The Tool: `semantic_search`

One simple tool with three parameters:

```python
semantic_search(
    query: str,          # Natural language query
    limit: int = 10,     # Max results (max: 100)
    threshold: float = 0.7  # Min similarity (0-1)
)
```

**Examples:**

```
semantic_search("database failures")
semantic_search("kubernetes scaling", limit=20)
semantic_search("cache problems", threshold=0.8)
```

**Returns:**

```
Found 5 results matching 'database failures':

1. **Redis Cache** [Service] (similarity: 0.923) - mentioned 15 times
2. **PostgreSQL** [Service] (similarity: 0.887) - mentioned 12 times
3. **cache timeout** [Action] (similarity: 0.845) - mentioned 8 times
4. **database connection pool** [GenericEntity] (similarity: 0.821)
5. **connection failures** [Metric] (similarity: 0.798) - mentioned 6 times
```

### How It Works

1. **Auto-discovers** all vector indexes in your database
2. **Generates** one embedding for your query (via OpenAI)
3. **Searches** all indexes in parallel
4. **Filters** by threshold
5. **Returns** top results sorted by similarity

No schema knowledge required!

## Prerequisites

Your Neo4j database needs:

1. **Nodes with embeddings** - Any nodes with an `embedding` property (list of floats)
2. **Vector indexes** - Created on the embedding properties

### Create Vector Indexes

```cypher
CREATE VECTOR INDEX my_index_name IF NOT EXISTS
FOR (n:MyNodeLabel) ON (n.embedding)
OPTIONS {indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
}}
```

Repeat for each node type that has embeddings.

## Testing

```bash
# Set environment variables
export OPENAI_API_KEY="sk-..."
export NEO4J_PASSWORD="your-password"

# Run test script
python mcp_servers/semantic_search/test_search.py
```

## Troubleshooting

### No results found

**Check:**
1. Neo4j is running
2. Vector indexes are created (`SHOW INDEXES` in Neo4j)
3. Nodes have embeddings populated
4. Try lowering the threshold (default: 0.7)

### Connection errors

**Check:**
- Neo4j URI is correct
- Neo4j password is correct
- Network connectivity
- Neo4j is running: `docker ps` or Neo4j Desktop

### MCP server not appearing

**Check:**
1. Claude Desktop config JSON is valid
2. `cwd` path is absolute and correct
3. Claude Desktop was restarted
4. Check Claude Desktop logs for errors

## Architecture

```
semantic_search/
├── config.py            # Environment configuration
├── semantic_search.py   # Core search engine
├── server.py            # MCP server
├── test_search.py       # Test script
└── README.md            # This file
```

### Key Features

- **Schema-agnostic**: Discovers indexes at runtime
- **Single embedding**: Generated once, used everywhere
- **Parallel search**: Searches all indexes simultaneously
- **Threshold filtering**: Only returns good matches
- **Error resilient**: Continues if one index fails
- **Simple interface**: One tool, three parameters

## Configuration Reference

### Environment Variables

```bash
# Required
OPENAI_API_KEY         # OpenAI API key for embeddings
NEO4J_PASSWORD         # Neo4j password

# Optional
NEO4J_URI              # Default: bolt://localhost:7687
NEO4J_USER             # Default: neo4j
EMBEDDING_MODEL        # Default: text-embedding-3-small
DEFAULT_LIMIT          # Default: 10
MAX_LIMIT              # Default: 100
```

### Tool Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *required* | Natural language query |
| `limit` | integer | 10 | Max results (max: 100) |
| `threshold` | float | 0.7 | Min similarity (0-1) |

### Threshold Guide

- **0.9+**: Very strict, near-exact matches
- **0.8-0.9**: Strong semantic similarity
- **0.7-0.8**: Good matches (default range)
- **0.6-0.7**: Loose matches, more results
- **<0.6**: Very loose, may include noise

## Examples

### Basic Search
```
semantic_search("monitoring alerts")
```

### Strict Matching
```
semantic_search("postgresql database", threshold=0.85)
```

### Broad Exploration
```
semantic_search("cloud infrastructure", limit=50, threshold=0.6)
```

## Development

To modify the tool:

1. Edit `semantic_search.py` to change search logic
2. Edit `server.py` to change tool interface
3. Run `test_search.py` to validate

## License

Part of the e2r-rd project.
