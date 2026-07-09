from datetime import datetime, timezone, timedelta

def get_text(props, key):
    try:
        items = props[key].get("title")
        if not items:
            return ""
        return items[0].get("plain_text", "")
    except:
        return ""

def get_rich_text(props, key):
    try:
        items = props[key]["rich_text"]
        if not items:
            return ""
        return items[0]["text"]["content"]
    except:
        return ""

def get_status(props, key):
    try:
        return props[key]["status"]["id"]
    except:
        return None

def get_status_name(props, key):
    try:
        return props[key]["status"]["name"]
    except:
        return None
    
def get_select( props, key):
    try:
        return props[key]["select"]["id"]
    except:
        return None
    
def get_select_name( props, key):
    try:
        return props[key]["select"]["name"]
    except:
        return None    
    
def get_date_time(page, key = "created_time"):
    try:
        dt_utc = datetime.fromisoformat(page["created_time"].replace("Z", "+00:00"))
        dt_kst = dt_utc.astimezone(timezone(timedelta(hours=9)))
        return dt_kst.strftime("%Y-%m-%d %H:%M")
    except:
        return None
    
def get_date(props, key):
    try:
        return props[key]["date"]["start"]
    except:
        return None    
    

from enum import Enum

class TodoPriority(str, Enum):
    '''Notion의 Priority에 보관된 값들'''
    P1="fieq"
    P2="n{DX"
    P3="vNZ~"
    P4="]_Hk"
    P5="]iH?"
    
    
# 편의를 위한 매핑    
# NOTION_PRIORITY_ID_MAP = {
#     TodoPriority.P1 : 'fieq',
#     TodoPriority.P2 : 'n{DX',
#     TodoPriority.P3 : 'vNZ~',
#     TodoPriority.P4 : ']_Hk',
#     TodoPriority.P5 : ']iH?'
# }

# 설명
NOTION_PRIORITY_VALUE_MAP = {
    TodoPriority.P1 : '긴급',
    TodoPriority.P2 : '높음',
    TodoPriority.P3 : '중간',
    TodoPriority.P4 : '낮음',
    TodoPriority.P5 : '매우 낮음'
}


# Notion option ID → Notodo priority 변환용 역방향 Map (e.g. 'fieq' → P1)
NOTION_PRIORITY_ID_REVERSE_MAP = {p.value: p for p in TodoPriority}

def to_notion_priority_id(priority: TodoPriority | str) -> str:
    """Notodo priority → Notion option ID (e.g. P1 → 'fieq')"""
    return TodoPriority[priority].value

def to_notion_priority_label(priority: TodoPriority | str | None) -> str:
    """Notodo priority → Notion 표시 레이블 (e.g. P1 → '긴급')
    """
    response = ""
    
    if priority and priority.strip() != "":
        response = NOTION_PRIORITY_VALUE_MAP[TodoPriority[priority]]

    return response


def from_notion_priority_id(option_id: str) -> str:
    """Notion option ID → Notodo priority 이름. option_id가 없으면 빈 문자열 반환 (e.g. 'fieq' → 'P1')"""
    if option_id :
        return NOTION_PRIORITY_ID_REVERSE_MAP[option_id].name
    else: 
        return ""
    
    
    
class TodoStatus(str, Enum):
    PENDING = "NCSy"
    IN_PROGRESS = "WNMd"
    COMPLETED = "klrZ"

NOTION_STATUS_VALUE_MAP = {
    TodoStatus.PENDING: "미시작",
    TodoStatus.IN_PROGRESS: "진행 중",
    TodoStatus.COMPLETED: "완료",
}


def to_notion_status_id(status: TodoStatus | str) -> str:
    """TodoStatus enum으로 Notion status ID를 반환. 예: PENDING → 'NCSy'"""
    return TodoStatus[status].value


def to_notion_status_label(status: TodoStatus | str | None) -> str:
    """TodoStatus enum으로 Notion에 표시되는 한글 레이블을 반환. 예: PENDING → '미시작'"""
    
    response = ""
    
    if status and status.strip() != "":
        response = NOTION_STATUS_VALUE_MAP[TodoStatus[status]]

    return response

NOTION_STATUS_ID_REVERSE_MAP = {s.value: s for s in TodoStatus}

# 역매핑(Notion → Notodo )
def from_notion_status_id(option_id: str) -> str:
    """Notion option id → Notodo status"""
    return NOTION_STATUS_ID_REVERSE_MAP[option_id].name

def sync_notion_status(status) :
    return to_notion_status_label(from_notion_status_id(status))
    
def sync_notion_priority(priority) :
    return to_notion_priority_label(from_notion_priority_id(priority))

