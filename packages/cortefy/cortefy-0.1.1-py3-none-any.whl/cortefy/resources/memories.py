"""
Memories resource for adding and managing memories
"""
from typing import Optional, List, Dict, Any


class MemoriesResource:
    """Resource for memory operations"""
    
    def __init__(self, client):
        self.client = client
    
    def add(
        self,
        content: str,
        container_tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_method: str = "tokens",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> dict:
        """
        Add a memory to the Cortefy API
        
        Args:
            content: The text content to store
            container_tags: List of container tags/names (uses first one if multiple)
            metadata: Optional metadata dictionary
            chunk_method: Chunking method ('tokens' or 'sentences')
            chunk_size: Size of chunks (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            
        Returns:
            Response dict with status, chunks, memory_ids, container, and timing
            
        Example:
            result = client.memories.add(
                content="Machine learning enables computers to learn from data",
                container_tags=["ai-research"],
                metadata={"priority": "high"}
            )
        """
        if not content:
            raise ValueError("content is required")
        
        # Use first container tag if multiple provided
        container = None
        if container_tags:
            if isinstance(container_tags, list) and len(container_tags) > 0:
                container = container_tags[0]
            elif isinstance(container_tags, str):
                container = container_tags
        
        payload = {
            "content": content,
            "metadata": metadata or {}
        }
        
        if container:
            payload["container"] = container
        
        if chunk_method:
            payload["chunk_method"] = chunk_method
        if chunk_size:
            payload["chunk_size"] = chunk_size
        if chunk_overlap:
            payload["chunk_overlap"] = chunk_overlap
        
        return self.client._request(
            method="POST",
            endpoint="/api/memories/ingest/",
            json=payload
        )

