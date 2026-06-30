from typing import Any, Dict

class NotionContainer:
    database: Dict[str, Any] | None = None
    data_sources: Dict[str, Any] | None = None

notion_container = NotionContainer()
