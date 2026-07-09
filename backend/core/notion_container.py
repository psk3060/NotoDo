from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class NotionContainer:
    database: Dict[str, Any] | None = None
    data_sources: list[Dict[str, Any]] = None

    @property
    def primary_data_source(self) -> Dict[str, Any] | None:
        return self.data_sources[0] if self.data_sources else None
    
    def get_data_source(self, source_id : str | None = None) -> Dict[str, Any] | None:
        if not self.data_sources:
            return None

        if source_id is None:
            return self.data_sources[0]
        return next((ds for ds in self.data_sources if ds.get("id") == source_id), None)