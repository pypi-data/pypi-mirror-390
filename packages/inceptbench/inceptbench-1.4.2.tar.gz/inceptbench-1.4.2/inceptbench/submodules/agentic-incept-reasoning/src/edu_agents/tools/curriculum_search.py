from __future__ import annotations

import logging
from typing import Callable

from ..core.tool_types import ToolResult
from .vector_store import search_vector_store

logger = logging.getLogger(__name__)

async def search_curriculum_standards(
    query: str,
    k: int = 6
) -> ToolResult:
    """
    Search the curriculum standards vector store and return the results.
    """
    logger.info(f"Searching curriculum standards for query: {query}")
    search_results = await search_vector_store(
        vector_store_id="vs_685b861800ec81918005402d28dcfe96",
        query=query,
        k=k
    )
    
    # Format the results with clear separators between documents
    if not search_results:
        formatted_text = "No curriculum standards found for the given query."
    else:
        formatted_parts = []
        for i, document in enumerate(search_results, 1):
            formatted_parts.append(f"=== CURRICULUM SEARCH RESULT {i} ===\n{document}")
        formatted_text = "\n\n".join(formatted_parts)
    
    return ToolResult(text=formatted_text, resp_id="curriculum_search")

def search_curriculum_tool() -> tuple[dict, Callable]:
    """
    Tool for searching curriculum standards.
    """
    spec = {
        "type": "function",
        "name": "search_curriculum_standards",
        "description": "Identify the most relevant curriculum standards and related information "
                       "for the given query. Can return multiple standards if relevant. Return "
                       "parameters can include Standard Descriptions, Learning Objectives, "
                       "Asssessment Boundaries, Common Misconceptions, Difficulty Definitions, "
                       "and other relevant information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language search query for finding relevant curriculum "
                                   "standards and related information."
                },
                "k": {
                    "type": "integer",
                    "description": "Number of standards to retrieve (default 6)",
                    "default": 6
                }
                },
            "required": ["query", "k"]
        }
    }
    return spec, search_curriculum_standards