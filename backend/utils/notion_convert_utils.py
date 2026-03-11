from enum import Enum

class TodoPriority(str, Enum):
    P1="fieq"
    P2="n{DX"
    P3="vNZ~"
    P4="]_Hk"
    P5="]iH?"
    
NOTION_PRIORITY_ID_MAP = {
    TodoPriority.P1 : 'fieq',
    TodoPriority.P2 : 'n{DX',
    TodoPriority.P3 : 'vNZ~',
    TodoPriority.P4 : ']_Hk',
    TodoPriority.P5 : ']iH?'
}

NOTION_PRIORITY_VALUE_MAP = {
    TodoPriority.P1 : '긴급',
    TodoPriority.P2 : '높음',
    TodoPriority.P3 : '중간',
    TodoPriority.P4 : '낮음',
    TodoPriority.P5 : '매우 낮음'
}

NOTION_PRIORITY_ID_REVERSE_MAP = {
    v: k for k, v in NOTION_PRIORITY_ID_MAP.items()
}

def to_notion_priority_id(priority: TodoPriority | str) -> str:
    """Notodo priority → Notion option id"""
    enum_priority = TodoPriority[priority]
    return NOTION_PRIORITY_ID_MAP[enum_priority]

def to_notion_priority_value(priority: TodoPriority | str) -> str:
    """List 시 사용 - Notodo priority → Notion option value"""
    enum_priority = TodoPriority[priority]
    return NOTION_PRIORITY_VALUE_MAP[enum_priority]

def from_notion_priority_id(option_id: str) -> str:
    """Notion option id → Notodo priority"""
    if option_id :
        return NOTION_PRIORITY_ID_REVERSE_MAP[option_id].name
    else: 
        return ""
    
    
    
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

def sync_notion_status(status) :
    return to_notion_status_value(from_notion_status_id(status))
    
def sync_notion_priority(priority) :
    return to_notion_priority_value(from_notion_priority_id(priority))
    