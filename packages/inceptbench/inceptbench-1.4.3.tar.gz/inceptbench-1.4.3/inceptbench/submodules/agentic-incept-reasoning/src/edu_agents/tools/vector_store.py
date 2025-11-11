from __future__ import annotations

import logging
from typing import List

from edu_agents.core.api_key_manager import get_async_openai_client

logger = logging.getLogger(__name__)


async def search_vector_store(
    vector_store_id: str,
    query: str,
    k: int = 6,
) -> List[str]:
    """
    Search a vector store and return the top k results as separate documents.
    
    Parameters
    ----------
    vector_store_id : str
        The ID of the vector store to search
    query : str
        The search query
    k : int, default 6
        Number of documents to return
        
    Returns
    -------
    List[str]
        List of up to k document texts from the vector store
    """
    documents: List[str] = []
    
    # Get async OpenAI client with API key rotation
    client = get_async_openai_client()
    
    page = await client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query
    )

    while True:
        items = getattr(page, "data", []) if not isinstance(page, dict) else page.get("data", [])

        for item in items:
            # Extract the complete text for this document/item
            document_text = ""
            
            if hasattr(item, "content"):
                # Concatenate all content parts for this single document
                content_parts = []
                for c in getattr(item, "content", []):
                    txt = getattr(c, "text", None)
                    if txt:
                        content_parts.append(txt)
                document_text = "".join(content_parts)
            elif isinstance(item, dict):
                document_text = (
                    item.get("document", {}).get("text") or 
                    (item.get("content") or [{}])[0].get("text", "")
                )
            
            if document_text:
                documents.append(document_text)
                
            if len(documents) >= k:
                break

        if len(documents) >= k or not getattr(page, "has_more", False):
            break

        next_cursor = getattr(page, "next_page", None)
        page = await client.vector_stores.search(
            vector_store_id=vector_store_id,
            query=query,
            page=next_cursor,
        )

    # De-duplicate results while preserving order
    deduped: List[str] = []
    seen: set[str] = set()
    for doc in documents:
        if doc not in seen:
            deduped.append(doc)
            seen.add(doc)
        if len(deduped) >= k:
            break

    return deduped