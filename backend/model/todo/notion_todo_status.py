from enum import Enum

class TodoStatus(str, Enum):
    PENDING = "NCSy"
    IN_PROGRESS = "WNMd"
    COMPLETED = "klrZ"

# 매핑용 Map(Notodo → Notion )
NOTION_STATUS_ID_MAP = {
    TodoStatus.PENDING: "NCSy",
    TodoStatus.IN_PROGRESS: "WNMd",
    TodoStatus.COMPLETED: "klrZ",
}

NOTION_STATUS_VALUE_MAP = {
    TodoStatus.PENDING: "미시작",
    TodoStatus.IN_PROGRESS: "진행 중",
    TodoStatus.COMPLETED: "완료",
}

def to_notion_status_id(status: TodoStatus | str) -> str:
    """Notodo status → Notion option id"""
    return NOTION_STATUS_ID_MAP[TodoStatus[status]]

def to_notion_status_value(status: TodoStatus | str) -> str:
    """List 시 사용 - Notodo status → Notion option value"""
    return NOTION_STATUS_VALUE_MAP[TodoStatus[status]]

# 매핑용 Map(Notion → Notodo )
NOTION_STATUS_ID_REVERSE_MAP = {
    v: k for k, v in NOTION_STATUS_ID_MAP.items()
}

# 역매핑(Notion → Notodo )
def from_notion_status_id(option_id: str) -> str:
    """Notion option id → Notodo status"""
    return NOTION_STATUS_ID_REVERSE_MAP[option_id].name
