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

NOTION_PRIORITY_ID_REVERSE_MAP = {
    v: k for k, v in NOTION_PRIORITY_ID_MAP.items()
}

def to_notion_priority_id(priority: TodoPriority | str) -> str:
    """Notodo priority → Notion option id"""
    enum_priority = TodoPriority[priority]
    return NOTION_PRIORITY_ID_MAP[enum_priority]

def from_notion_priority_id(option_id: str) -> str:
    """Notion option id → Notodo priority"""
    if option_id :
        return NOTION_PRIORITY_ID_REVERSE_MAP[option_id].name
    else: 
        return ""