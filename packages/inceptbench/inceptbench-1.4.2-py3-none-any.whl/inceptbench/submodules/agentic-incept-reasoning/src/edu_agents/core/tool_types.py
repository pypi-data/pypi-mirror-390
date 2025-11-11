from dataclasses import dataclass

@dataclass
class ToolResult:
    """Return value for a guidance tool."""
    text: str       # bullet-list guidance
    resp_id: str    # response.id produced by the tool 