from datetime import datetime, timezone, timedelta

def get_text(props, key):
    try:
        items = props[key].get("title") or props[key].get("rich_text")
        if not items:
            return ""
        return items[0].get("plain_text", "")
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
    

