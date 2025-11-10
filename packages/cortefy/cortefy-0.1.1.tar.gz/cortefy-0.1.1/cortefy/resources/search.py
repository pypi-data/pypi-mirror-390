"""
Search resource for querying memories
"""
from typing import Optional


class SearchResource:
    """Resource for search operations"""
    
    def __init__(self, client):
        self.client = client
    
    def memories(
        self,
        q: str,
        container_tag: Optional[str] = None,
        limit: int = 5,
        min_similarity: float = 0.0
    ) -> dict:
        """
        Search memories using semantic search
        
        Args:
            q: Search query text
            container_tag: Optional container tag to filter by
            limit: Maximum number of results (default: 5)
            min_similarity: Minimum similarity score (0.0 to 1.0, default: 0.0)
            
        Returns:
            Response dict with results, timing, and total count
            
        Example:
            results = client.search.memories(
                q="machine learning accuracy",
                limit=5,
                container_tag="research"
            )
        """
        if not q:
            raise ValueError("query (q) is required")
        
        payload = {
            "q": q,
            "limit": limit,
            "min_similarity": min_similarity
        }
        
        if container_tag:
            payload["containerTag"] = container_tag
        
        return self.client._request(
            method="POST",
            endpoint="/api/memories/search/",
            json=payload
        )

