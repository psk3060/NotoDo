from typing import Any, Dict

class NotionState:
    database: Dict[str, Any] | None = None
    data_sources: Dict[str, Any] | None = None

notion_state = NotionState()